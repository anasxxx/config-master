import { CardProduct } from './card-product.model';
import { NewBranchModule } from './new-branch-module.model';
import { MigResourcesModule } from './mig-resources-module.model';
import { Currency } from './currency.model';
import { Country } from './country.model';

export class BankReq {
  pBusinessDate!: string;
  pBankCode!: string;
  pBankWording!: string;
  pCurrencyCode!: string;
  pCountryCode!: string;
  p_action_flag!: string;
  cardProducts!: CardProduct[];
  branches!: NewBranchModule[];
  ressources!: MigResourcesModule[];
}

export interface BankWithUI extends BankReq {
  isExpanded: boolean;
  accountCount: number;
  lastUpdated: string;
  country?: Country;
  currency?: Currency;
}
