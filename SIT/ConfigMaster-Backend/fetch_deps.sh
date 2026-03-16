#!/bin/bash
# Iterative Maven dependency fetcher via curl
# Downloads POMs and JARs from Maven Central when Java DNS is broken

REPO="https://repo1.maven.org/maven2"
LOCAL="$HOME/.m2/repository"
PROJECT_DIR="/home/user/config-master/SIT/ConfigMaster-Backend"

download_artifact() {
    local group="$1" artifact="$2" version="$3" ext="$4"
    local group_path="${group//\.//}"
    local dir="$LOCAL/$group_path/$artifact/$version"
    local file="$artifact-$version.$ext"
    local url="$REPO/$group_path/$artifact/$version/$file"
    local target="$dir/$file"

    if [ -f "$target" ]; then
        return 0
    fi

    mkdir -p "$dir"
    local http_code
    http_code=$(curl -s -o "$target" -w "%{http_code}" "$url")
    if [ "$http_code" = "200" ]; then
        echo "  OK: $group:$artifact:$version ($ext)"
        return 0
    else
        rm -f "$target"
        return 1
    fi
}

# Also download hash files for verification
download_hashes() {
    local group="$1" artifact="$2" version="$3" ext="$4"
    local group_path="${group//\.//}"
    local dir="$LOCAL/$group_path/$artifact/$version"
    local file="$artifact-$version.$ext"
    for hash_ext in sha1; do
        local url="$REPO/$group_path/$artifact/$version/$file.$hash_ext"
        local target="$dir/$file.$hash_ext"
        if [ ! -f "$target" ]; then
            curl -s -o "$target" -w "" "$url"
            # Don't check status - hash files are optional
        fi
    done
}

# Clear resolver-status.properties files that block offline resolution
clear_resolver_status() {
    find "$LOCAL" -name "*.lastUpdated" -delete 2>/dev/null
    find "$LOCAL" -name "_remote.repositories" -delete 2>/dev/null
    find "$LOCAL" -name "resolver-status.properties" -delete 2>/dev/null
}

# Parse POM for parent and dependency imports
parse_pom_parents() {
    local pomfile="$1"
    if [ ! -f "$pomfile" ]; then
        return
    fi
    # Extract parent groupId, artifactId, version
    python3 -c "
import xml.etree.ElementTree as ET
import sys

ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
try:
    tree = ET.parse('$pomfile')
    root = tree.getroot()
    # Parent
    parent = root.find('m:parent', ns)
    if parent is not None:
        g = parent.find('m:groupId', ns)
        a = parent.find('m:artifactId', ns)
        v = parent.find('m:version', ns)
        if g is not None and a is not None and v is not None:
            print(f'{g.text}:{a.text}:pom:{v.text}')
    # Import BOMs in dependencyManagement
    dm = root.find('.//m:dependencyManagement', ns)
    if dm is not None:
        for dep in dm.findall('.//m:dependency', ns):
            scope = dep.find('m:scope', ns)
            typ = dep.find('m:type', ns)
            if scope is not None and scope.text == 'import' and typ is not None and typ.text == 'pom':
                g = dep.find('m:groupId', ns)
                a = dep.find('m:artifactId', ns)
                v = dep.find('m:version', ns)
                if g is not None and a is not None and v is not None:
                    print(f'{g.text}:{a.text}:pom:{v.text}')
except Exception as e:
    pass
" 2>/dev/null
}

echo "=== Phase 1: Download all BOM POMs from spring-boot-dependencies ==="
BOMS=(
    "io.micrometer:micrometer-tracing-bom:pom:1.2.2"
    "org.mockito:mockito-bom:pom:5.7.0"
    "io.netty:netty-bom:pom:4.1.105.Final"
    "com.squareup.okhttp3:okhttp-bom:pom:4.12.0"
    "io.opentelemetry:opentelemetry-bom:pom:1.31.0"
    "com.oracle.database.jdbc:ojdbc-bom:pom:21.9.0.0"
    "io.prometheus:simpleclient_bom:pom:0.16.0"
    "com.querydsl:querydsl-bom:pom:5.0.0"
    "io.projectreactor:reactor-bom:pom:2023.0.2"
    "io.rest-assured:rest-assured-bom:pom:5.3.2"
    "io.rsocket:rsocket-bom:pom:1.1.3"
    "org.seleniumhq.selenium:selenium-bom:pom:4.14.1"
    "org.springframework.amqp:spring-amqp-bom:pom:3.1.1"
    "org.springframework.batch:spring-batch-bom:pom:5.1.0"
    "org.springframework.data:spring-data-bom:pom:2023.1.2"
    "org.springframework.integration:spring-integration-bom:pom:6.2.1"
    "org.springframework.pulsar:spring-pulsar-bom:pom:1.0.2"
    "org.springframework.restdocs:spring-restdocs-bom:pom:3.0.1"
    "org.springframework.security:spring-security-bom:pom:6.2.1"
    "org.springframework.session:spring-session-bom:pom:3.2.1"
    "org.springframework.ws:spring-ws-bom:pom:4.0.10"
    "org.testcontainers:testcontainers-bom:pom:1.19.3"
    "com.datastax.oss:java-driver-bom:pom:4.17.0"
    "com.fasterxml.jackson:jackson-bom:pom:2.15.3"
    "io.dropwizard.metrics:metrics-bom:pom:4.2.23"
    "io.micrometer:micrometer-bom:pom:1.12.2"
    "io.zipkin.brave:brave-bom:pom:5.16.0"
    "org.apache.groovy:groovy-bom:pom:4.0.17"
    "org.apache.logging.log4j:log4j-bom:pom:2.21.1"
    "org.assertj:assertj-bom:pom:3.24.2"
    "org.eclipse.jetty.ee10:jetty-ee10-bom:pom:12.0.5"
    "org.eclipse.jetty:jetty-bom:pom:12.0.5"
    "org.glassfish.jaxb:jaxb-bom:pom:4.0.4"
    "org.glassfish.jersey:jersey-bom:pom:3.1.5"
    "org.infinispan:infinispan-bom:pom:14.0.21.Final"
    "org.jetbrains.kotlin:kotlin-bom:pom:1.9.22"
    "org.jetbrains.kotlinx:kotlinx-coroutines-bom:pom:1.7.3"
    "org.jetbrains.kotlinx:kotlinx-serialization-bom:pom:1.6.2"
    "org.junit:junit-bom:pom:5.10.1"
    # Additional parent POMs
    "org.springframework:spring-framework-bom:pom:6.1.3"
)

for coord in "${BOMS[@]}"; do
    IFS=':' read -r g a t v <<< "$coord"
    download_artifact "$g" "$a" "$v" "pom"
done

echo ""
echo "=== Phase 1b: Download parent POMs of the BOMs ==="
# Recursively fetch parent POMs
declare -A SEEN
fetch_parents_recursive() {
    local group="$1" artifact="$2" version="$3"
    local key="$group:$artifact:$version"
    if [[ -n "${SEEN[$key]}" ]]; then return; fi
    SEEN[$key]=1

    local group_path="${group//\.//}"
    local pomfile="$LOCAL/$group_path/$artifact/$version/$artifact-$version.pom"

    download_artifact "$group" "$artifact" "$version" "pom"

    if [ -f "$pomfile" ]; then
        while IFS= read -r line; do
            if [ -z "$line" ]; then continue; fi
            IFS=':' read -r pg pa pt pv <<< "$line"
            download_artifact "$pg" "$pa" "$pv" "pom"
            fetch_parents_recursive "$pg" "$pa" "$pv"
        done < <(parse_pom_parents "$pomfile")
    fi
}

for coord in "${BOMS[@]}"; do
    IFS=':' read -r g a t v <<< "$coord"
    fetch_parents_recursive "$g" "$a" "$v"
done

echo ""
echo "=== Phase 2: Iterative Maven resolution ==="
MAX_ITERATIONS=20
for iteration in $(seq 1 $MAX_ITERATIONS); do
    echo ""
    echo "--- Iteration $iteration ---"

    clear_resolver_status

    # Run Maven and capture output
    OUTPUT=$(cd "$PROJECT_DIR" && mvn spring-boot:run -o 2>&1)

    # Check if build started successfully (compilation phase reached)
    if echo "$OUTPUT" | grep -q "BUILD SUCCESS\|Compiling\|Started ConfigmasterBackendApplication\|spring-boot:run.*running"; then
        echo "Maven build progressing! Checking if app started..."
        if echo "$OUTPUT" | grep -q "BUILD SUCCESS"; then
            echo "BUILD SUCCESS!"
            exit 0
        fi
    fi

    # Extract missing artifacts - multiple patterns
    MISSING=$(echo "$OUTPUT" | grep -oP '(?<=resolved: )\S+:\S+:\S+:\S+' | sort -u)

    if [ -z "$MISSING" ]; then
        # Try another pattern for plugin resolution
        MISSING=$(echo "$OUTPUT" | grep -oP 'artifact \S+:\S+:\S+:\S+ ' | sed 's/artifact //' | tr -d ' ' | sort -u)
    fi

    if [ -z "$MISSING" ]; then
        # Try pattern for missing plugins
        MISSING=$(echo "$OUTPUT" | grep -oP '\S+:\S+:jar:\S+ has not been downloaded' | sed 's/ has not been downloaded//' | sed 's/:jar:/:jar:/' | sort -u)
    fi

    if [ -z "$MISSING" ]; then
        echo "No more missing artifacts detected."
        echo "Last Maven output (tail):"
        echo "$OUTPUT" | tail -20
        break
    fi

    COUNT=$(echo "$MISSING" | wc -l)
    echo "Found $COUNT missing artifacts"

    NEW_DOWNLOADS=0
    while IFS= read -r coord; do
        [ -z "$coord" ] && continue
        # Parse group:artifact:type:version or group:artifact:type:classifier:version
        IFS=':' read -r g a t rest <<< "$coord"
        # rest could be "version" or "classifier:version"
        if [[ "$rest" == *:* ]]; then
            IFS=':' read -r classifier v <<< "$rest"
        else
            v="$rest"
            classifier=""
        fi

        # Remove trailing junk like "(absent)"
        v=$(echo "$v" | sed 's/ .*//')

        # Download POM
        if download_artifact "$g" "$a" "$v" "pom"; then
            NEW_DOWNLOADS=$((NEW_DOWNLOADS + 1))
            download_hashes "$g" "$a" "$v" "pom"
            # Fetch parents recursively
            fetch_parents_recursive "$g" "$a" "$v"
        fi

        # Download JAR if type is jar
        if [ "$t" = "jar" ]; then
            if download_artifact "$g" "$a" "$v" "jar"; then
                NEW_DOWNLOADS=$((NEW_DOWNLOADS + 1))
                download_hashes "$g" "$a" "$v" "jar"
            fi
        fi
    done <<< "$MISSING"

    if [ "$NEW_DOWNLOADS" -eq 0 ]; then
        echo "No new downloads in this iteration. Trying non-offline approach..."
        echo "Last Maven output (tail):"
        echo "$OUTPUT" | tail -30
        break
    fi

    echo "Downloaded $NEW_DOWNLOADS new artifacts"
done

echo ""
echo "=== Final: Attempt mvn spring-boot:run -o ==="
clear_resolver_status
cd "$PROJECT_DIR" && mvn spring-boot:run -o 2>&1 | tail -30
