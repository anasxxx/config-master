import { MigBinRangePlasticProdModule } from './mig-bin-range-plastic-prod-module.model';
import { PreMigCardFeesModule } from './pre-mig-card-fees-module.model';
import { MigServiceProdModule } from './mig-service-prod-module.model';
import { MigLimitStandModule } from './mig-limit-stand-module.model';

export class CardProduct {
  info!: MigBinRangePlasticProdModule;
  fees!: PreMigCardFeesModule;
  services!: MigServiceProdModule;
  limits!: MigLimitStandModule[];
}
