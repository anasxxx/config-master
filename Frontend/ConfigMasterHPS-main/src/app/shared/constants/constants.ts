// constants.ts

export const HARDCODED_RESOURCE_WORDINGS: string[] = [
    'MCD_MDS',
    'MCD_CIS',
    'UPI',
    'HOST_BANK',
    'SID',
    'VISA_SMS',
    'VISA_BASE1',
  ];
  
  export const SERVICES = [
    { name: 'retrait', label: 'banks.add.step2.retrait', icon: 'bi-arrow-down-circle' },
    { name: 'achat', label: 'banks.add.step2.achat', icon: 'bi-bag' },
    { name: 'advance', label: 'banks.add.step2.advance', icon: 'bi-cash-stack' },
    { name: 'ecommerce', label: 'banks.add.step2.ecommerce', icon: 'bi-cart' },
    { name: 'transfert', label: 'banks.add.step2.transfert', icon: 'bi-arrow-left-right' },
    { name: 'quasicash', label: 'banks.add.step2.quasicash', icon: 'bi-coin' },
    { name: 'solde', label: 'banks.add.step2.solde', icon: 'bi-wallet' },
    { name: 'releve', label: 'banks.add.step2.releve', icon: 'bi-file-text' },
    { name: 'pinchange', label: 'banks.add.step2.pinchange', icon: 'bi-lock' },
    { name: 'refund', label: 'banks.add.step2.refund', icon: 'bi-arrow-counterclockwise' },
    { name: 'moneysend', label: 'banks.add.step2.moneysend', icon: 'bi-send' },
    { name: 'billpayment', label: 'banks.add.step2.billpayment', icon: 'bi-receipt' },
    { name: 'original', label: 'banks.add.step2.original', icon: 'bi-check-circle' },
    { name: 'authentication', label: 'banks.add.step2.authentication', icon: 'bi-shield-lock' },
    { name: 'cashback', label: 'banks.add.step2.cashback', icon: 'bi-cash-coin' },
  ];
  
  export const NETWORKS = [
    'VISA',
    'PRIVATIVE',
    'GIMN',
    'AMEX',
    'MCRD',
    'EUROPAY',
    'TAG-YUP',
    'DINERS',
    'UPI'
  ]

  export const LIMITS =[
    {id : '10', label : 'Default'},
    {id : '1', label : 'Retrait'},
    {id : '2', label : 'Purchase'},
    {id : '3', label : 'CASH_advance'},
    {id : '4', label : 'Quasi-cash'},
    {id : '9', label : 'E-commerce'}
  ]