#!/usr/bin/env python3
"""Recursively download all Maven dependencies via curl."""
import os
import subprocess
import xml.etree.ElementTree as ET
import re
import sys
from collections import deque

REPO = "https://repo1.maven.org/maven2"
LOCAL = os.path.expanduser("~/.m2/repository")
NS = {'m': 'http://maven.apache.org/POM/4.0.0'}

downloaded = set()
failed = set()


def artifact_path(group, artifact, version, ext):
    gpath = group.replace('.', '/')
    return f"{gpath}/{artifact}/{version}/{artifact}-{version}.{ext}"


def local_path(group, artifact, version, ext):
    return os.path.join(LOCAL, artifact_path(group, artifact, version, ext))


def download(group, artifact, version, ext):
    key = f"{group}:{artifact}:{version}:{ext}"
    if key in downloaded or key in failed:
        return key in downloaded

    lp = local_path(group, artifact, version, ext)
    if os.path.exists(lp) and os.path.getsize(lp) > 0:
        downloaded.add(key)
        return True

    url = f"{REPO}/{artifact_path(group, artifact, version, ext)}"
    os.makedirs(os.path.dirname(lp), exist_ok=True)

    result = subprocess.run(
        ["curl", "-sf", "-o", lp, url],
        capture_output=True, timeout=30
    )

    if result.returncode == 0 and os.path.exists(lp) and os.path.getsize(lp) > 0:
        downloaded.add(key)
        print(f"  OK: {group}:{artifact}:{version} ({ext})")
        return True
    else:
        if os.path.exists(lp):
            os.remove(lp)
        failed.add(key)
        print(f"  FAIL: {group}:{artifact}:{version} ({ext})")
        return False


def resolve_property(text, properties):
    """Resolve ${property} references."""
    if not text or '${' not in text:
        return text
    for _ in range(5):  # max depth
        m = re.search(r'\$\{([^}]+)\}', text)
        if not m:
            break
        prop_name = m.group(1)
        if prop_name in properties:
            text = text.replace(f'${{{prop_name}}}', properties[prop_name])
        else:
            break
    return text


def parse_pom(pomfile, properties=None):
    """Parse a POM file and return (parent_coords, bom_coords, dep_coords, properties)."""
    if properties is None:
        properties = {}

    parents = []
    boms = []
    deps = []

    if not os.path.exists(pomfile):
        return parents, boms, deps, properties

    try:
        tree = ET.parse(pomfile)
        root = tree.getroot()
    except ET.ParseError:
        return parents, boms, deps, properties

    # Extract properties
    props_el = root.find('m:properties', NS)
    if props_el is not None:
        for child in props_el:
            tag = child.tag.replace(f'{{{NS["m"]}}}', '')
            if child.text:
                properties[tag] = child.text.strip()

    # Also get version from this POM
    ver_el = root.find('m:version', NS)
    if ver_el is not None and ver_el.text:
        properties['project.version'] = ver_el.text.strip()
        properties['pom.version'] = ver_el.text.strip()

    gid_el = root.find('m:groupId', NS)
    if gid_el is not None and gid_el.text:
        properties['project.groupId'] = gid_el.text.strip()
        properties['pom.groupId'] = gid_el.text.strip()

    # Parent
    parent = root.find('m:parent', NS)
    if parent is not None:
        g = parent.findtext('m:groupId', namespaces=NS)
        a = parent.findtext('m:artifactId', namespaces=NS)
        v = parent.findtext('m:version', namespaces=NS)
        if g and a and v:
            g, a, v = g.strip(), a.strip(), v.strip()
            parents.append((g, a, v))
            # Inherit parent version as property
            if 'project.version' not in properties:
                properties['project.version'] = v
                properties['pom.version'] = v
            if 'project.groupId' not in properties:
                properties['project.groupId'] = g
                properties['pom.groupId'] = g

    # Import BOMs in dependencyManagement
    dm = root.find('.//m:dependencyManagement', NS)
    if dm is not None:
        for dep in dm.findall('.//m:dependency', NS):
            scope = dep.findtext('m:scope', namespaces=NS)
            typ = dep.findtext('m:type', namespaces=NS)
            if scope and scope.strip() == 'import' and typ and typ.strip() == 'pom':
                g = dep.findtext('m:groupId', namespaces=NS)
                a = dep.findtext('m:artifactId', namespaces=NS)
                v = dep.findtext('m:version', namespaces=NS)
                if g and a and v:
                    g = resolve_property(g.strip(), properties)
                    a = resolve_property(a.strip(), properties)
                    v = resolve_property(v.strip(), properties)
                    if '${' not in v:  # Only if fully resolved
                        boms.append((g, a, v))

    # Direct dependencies
    deps_el = root.find('m:dependencies', NS)
    if deps_el is not None:
        for dep in deps_el.findall('m:dependency', NS):
            g = dep.findtext('m:groupId', namespaces=NS)
            a = dep.findtext('m:artifactId', namespaces=NS)
            v = dep.findtext('m:version', namespaces=NS)
            typ = dep.findtext('m:type', namespaces=NS) or 'jar'
            scope = dep.findtext('m:scope', namespaces=NS) or 'compile'
            if g and a and v:
                g = resolve_property(g.strip(), properties)
                a = resolve_property(a.strip(), properties)
                v = resolve_property(v.strip(), properties)
                typ = typ.strip()
                scope = scope.strip()
                if '${' not in v:  # Only if fully resolved
                    deps.append((g, a, v, typ, scope))

    return parents, boms, deps, properties


def fetch_pom_tree(group, artifact, version):
    """Recursively fetch a POM and all its parents/BOMs."""
    queue = deque([(group, artifact, version)])
    seen = set()

    while queue:
        g, a, v = queue.popleft()
        key = f"{g}:{a}:{v}"
        if key in seen:
            continue
        seen.add(key)

        download(g, a, v, "pom")

        pomfile = local_path(g, a, v, "pom")
        parents, boms, deps, props = parse_pom(pomfile)

        for pg, pa, pv in parents:
            if f"{pg}:{pa}:{pv}" not in seen:
                queue.append((pg, pa, pv))

        for bg, ba, bv in boms:
            if f"{bg}:{ba}:{bv}" not in seen:
                queue.append((bg, ba, bv))


def main():
    # Phase 1: Clean up resolver status files
    print("=== Cleaning resolver status files ===")
    for root_dir, dirs, files in os.walk(LOCAL):
        for f in files:
            if f.endswith('.lastUpdated') or f == '_remote.repositories' or f == 'resolver-status.properties':
                os.remove(os.path.join(root_dir, f))

    # Phase 2: Start from project POM and spring-boot-starter-parent
    print("\n=== Phase 1: Fetch parent POM chain ===")
    fetch_pom_tree("org.springframework.boot", "spring-boot-starter-parent", "3.2.2")
    fetch_pom_tree("org.springframework.boot", "spring-boot-dependencies", "3.2.2")

    # Phase 3: Parse spring-boot-dependencies to get ALL BOMs
    print("\n=== Phase 2: Fetch all BOMs from spring-boot-dependencies ===")
    dep_pom = local_path("org.springframework.boot", "spring-boot-dependencies", "3.2.2", "pom")
    parents, boms, deps, props = parse_pom(dep_pom)

    print(f"Found {len(boms)} BOMs in spring-boot-dependencies")
    for g, a, v in boms:
        fetch_pom_tree(g, a, v)

    # Phase 4: Now iteratively run Maven and download what's missing
    print("\n=== Phase 3: Iterative Maven resolution ===")
    project_dir = "/home/user/config-master/SIT/ConfigMaster-Backend"

    for iteration in range(1, 50):
        print(f"\n--- Iteration {iteration} ---")

        # Clean resolver status
        for root_dir, dirs, files in os.walk(LOCAL):
            for f in files:
                if f.endswith('.lastUpdated') or f == '_remote.repositories' or f == 'resolver-status.properties':
                    os.remove(os.path.join(root_dir, f))

        result = subprocess.run(
            ["mvn", "spring-boot:run", "-o"],
            capture_output=True, text=True, cwd=project_dir, timeout=120
        )

        output = result.stdout + result.stderr

        if "BUILD SUCCESS" in output or "Started" in output:
            print("BUILD SUCCESS!")
            return 0

        # Check if we got to compilation
        if "Compiling" in output or "BUILD FAILURE" in output:
            # Check for compilation errors vs dependency errors
            if "Could not resolve dependencies" not in output and \
               "could not be resolved" not in output and \
               "is missing" not in output and \
               "Non-resolvable" not in output:
                print("No more dependency issues. Build output:")
                # Print last 30 lines
                lines = output.strip().split('\n')
                for line in lines[-40:]:
                    print(line)
                return 0

        # Extract missing artifacts with various patterns
        missing = set()

        # Pattern 1: "could not be resolved: GROUP:ART:TYPE:VER (absent)"
        for m in re.finditer(r'(?:could not be resolved|resolved): (\S+?):(\S+?):(\S+?):(\S+?)[\s(]', output):
            g, a, t, v = m.groups()
            v = v.rstrip(')')
            missing.add((g, a, v, t))

        # Pattern 2: "The POM for GROUP:ART:TYPE:VER is missing"
        for m in re.finditer(r'The POM for (\S+?):(\S+?):(\S+?):(\S+?) is missing', output):
            g, a, t, v = m.groups()
            missing.add((g, a, v, t))

        # Pattern 3: Plugin resolution - "artifact GROUP:ART:TYPE:VER"
        for m in re.finditer(r'artifact (\S+?):(\S+?):(\S+?):(\S+?) has not been downloaded', output):
            g, a, t, v = m.groups()
            missing.add((g, a, v, t))

        # Pattern 4: "Non-resolvable parent POM"
        for m in re.finditer(r'Non-resolvable.*?(\S+?):(\S+?):pom:(\S+?)[\s)]', output):
            g, a, v = m.groups()
            missing.add((g, a, v, 'pom'))

        if not missing:
            print("No missing artifacts detected. Output tail:")
            lines = output.strip().split('\n')
            for line in lines[-30:]:
                print(line)
            break

        print(f"Found {len(missing)} missing artifacts")
        new_downloads = 0

        for g, a, v, t in sorted(missing):
            # Always download POM
            if download(g, a, v, "pom"):
                new_downloads += 1
                # Recursively fetch parent chain
                fetch_pom_tree(g, a, v)

            # Download JAR if type is jar
            if t == 'jar':
                if download(g, a, v, "jar"):
                    new_downloads += 1

        if new_downloads == 0:
            print("No new downloads. Output tail:")
            lines = output.strip().split('\n')
            for line in lines[-30:]:
                print(line)
            break

        print(f"Downloaded {new_downloads} new files")

    # Final attempt
    print("\n=== Final attempt ===")
    for root_dir, dirs, files in os.walk(LOCAL):
        for f in files:
            if f.endswith('.lastUpdated') or f == '_remote.repositories' or f == 'resolver-status.properties':
                os.remove(os.path.join(root_dir, f))

    result = subprocess.run(
        ["mvn", "spring-boot:run", "-o"],
        capture_output=True, text=True, cwd=project_dir, timeout=120
    )
    output = result.stdout + result.stderr
    lines = output.strip().split('\n')
    for line in lines[-40:]:
        print(line)

    return result.returncode


if __name__ == '__main__':
    sys.exit(main())
