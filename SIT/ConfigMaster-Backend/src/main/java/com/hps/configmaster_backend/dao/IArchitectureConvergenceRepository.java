package com.hps.configmaster_backend.dao;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.hps.configmaster_backend.entity.ArchitectureConvergence;
import com.hps.configmaster_backend.models.ArchetecteurModule;

@Repository
public interface IArchitectureConvergenceRepository extends JpaRepository<ArchitectureConvergence, String> {
    @Query("SELECT new com.hps.configmaster_backend.models.ArchetecteurModule(" +
           "a.resourceId, a.libelle, b.resourceLive, b.prisProcessingStep, b.prisConnectMode) " +
           "FROM ArchitectureConvergence a " +
           "JOIN a.resource b " +
           "WHERE a.resourceId = b.resource_id " +  // Changé de b.resourceId à b.resource_id
           "AND a.nodeId = b.node_id " +           // Changé de b.nodeId à b.node_id
           "AND a.nodeId = '0001' " +
           "AND SUBSTR(b.wording, 1, 3) = SUBSTR(:codeBank, 1, 3)")
    List<ArchetecteurModule> findArchitectureNode1(@Param("codeBank") String codeBank);

    @Query("SELECT new com.hps.configmaster_backend.models.ArchetecteurModule(" +
           "a.resourceId, a.libelle, b.resourceLive, b.prisProcessingStep, b.prisConnectMode) " +
           "FROM ArchitectureConvergence a " +
           "JOIN a.resource b " +
           "WHERE a.resourceId = b.resource_id " +  // Changé de b.resourceId à b.resource_id
           "AND a.nodeId = b.node_id " +           // Changé de b.nodeId à b.node_id
           "AND a.nodeId = '0002' " +
           "AND SUBSTR(b.wording, 1, 3) = SUBSTR(:codeBank, 1, 3)")
    List<ArchetecteurModule> findArchitectureNode2(@Param("codeBank") String codeBank);
}