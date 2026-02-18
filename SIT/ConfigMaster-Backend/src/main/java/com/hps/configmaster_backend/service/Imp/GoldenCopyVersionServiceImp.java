package com.hps.configmaster_backend.service.Imp;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.hps.configmaster_backend.dao.IGoldenCopyVersionRepository;
import com.hps.configmaster_backend.dao.IMetadataRepository;
import com.hps.configmaster_backend.entity.GoldenCopyVersion;
import com.hps.configmaster_backend.models.PackageModule;
import com.hps.configmaster_backend.service.IGoldenCopyVersionService;

@Service
public class GoldenCopyVersionServiceImp implements IGoldenCopyVersionService {

    @Autowired
    private IGoldenCopyVersionRepository goldenCopyVersionRepository;

    @Autowired
    private IMetadataRepository metadataRepository;

    @Override
    public String saveGoldenCopyVersion(String description) {
        Optional<GoldenCopyVersion> latest = goldenCopyVersionRepository.findTopByOrderByIdDesc();

        int nextVersionNumber = 1;
        int nextExtensionNumber = 40601;

        if (latest.isPresent()) {
            String lastVersionId = latest.get().getVersion_id();        // ex : "V10"
            String lastExtensionName = latest.get().getExtension_name(); // ex : "040610"

            // Incrément version_id : "V" + (nombre + 1)
            if (lastVersionId != null && lastVersionId.trim().matches("V\\d+")) {
                nextVersionNumber = Integer.parseInt(lastVersionId.trim().substring(1)) + 1;
            }

            // Incrément extension_name
            if (lastExtensionName != null && lastExtensionName.matches("\\d+")) {
                nextExtensionNumber = Integer.parseInt(lastExtensionName) + 1;
            }
        }

        String newVersionId = "V" + nextVersionNumber;
        String newExtensionName = String.format("%06d", nextExtensionNumber);

        GoldenCopyVersion gcv = new GoldenCopyVersion();
        gcv.setVersion_id(newVersionId); // <- Clé primaire générée ici
        gcv.setExtension_name(newExtensionName);
        gcv.setDate(LocalDateTime.now());
gcv.setDescription(description);
        goldenCopyVersionRepository.save(gcv);

        return newExtensionName;
    }


    @Override
    public byte[] exportAsZip(String description) {
        List<PackageModule> packages = metadataRepository.getFilteredPackages();

        String newVersion = saveGoldenCopyVersion(description); // récupérer la version ici
        ByteArrayOutputStream baos = new ByteArrayOutputStream();

        try (ZipOutputStream zos = new ZipOutputStream(baos)) {
            for (PackageModule pkg : packages) {
                String fileName = pkg.getName() + "_" + newVersion + ".sql";
                ZipEntry entry = new ZipEntry(fileName);
                zos.putNextEntry(entry);
                zos.write(pkg.getDdl().getBytes(StandardCharsets.UTF_8));
                zos.closeEntry();
            }
        } catch (IOException e) {
            throw new RuntimeException("Erreur lors de la création du ZIP", e);
        }

        return baos.toByteArray();
    }
}
