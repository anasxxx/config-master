import { BatchResult } from "./batchResult.model";
import { RapportResult } from "./RapportResult.model";

export interface SimulationResult {
    batcheResultModule : BatchResult[];
    failedReports : RapportResult[];
}