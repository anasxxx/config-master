'use strict';

customElements.define('compodoc-menu', class extends HTMLElement {
    constructor() {
        super();
        this.isNormalMode = this.getAttribute('mode') === 'normal';
    }

    connectedCallback() {
        this.render(this.isNormalMode);
    }

    render(isNormalMode) {
        let tp = lithtml.html(`
        <nav>
            <ul class="list">
                <li class="title">
                    <a href="index.html" data-type="index-link">config-master documentation</a>
                </li>

                <li class="divider"></li>
                ${ isNormalMode ? `<div id="book-search-input" role="search"><input type="text" placeholder="Type to search"></div>` : '' }
                <li class="chapter">
                    <a data-type="chapter-link" href="index.html"><span class="icon ion-ios-home"></span>Getting started</a>
                    <ul class="links">
                        <li class="link">
                            <a href="overview.html" data-type="chapter-link">
                                <span class="icon ion-ios-keypad"></span>Overview
                            </a>
                        </li>
                        <li class="link">
                            <a href="index.html" data-type="chapter-link">
                                <span class="icon ion-ios-paper"></span>README
                            </a>
                        </li>
                                <li class="link">
                                    <a href="dependencies.html" data-type="chapter-link">
                                        <span class="icon ion-ios-list"></span>Dependencies
                                    </a>
                                </li>
                                <li class="link">
                                    <a href="properties.html" data-type="chapter-link">
                                        <span class="icon ion-ios-apps"></span>Properties
                                    </a>
                                </li>
                    </ul>
                </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#components-links"' :
                            'data-bs-target="#xs-components-links"' }>
                            <span class="icon ion-md-cog"></span>
                            <span>Components</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="components-links"' : 'id="xs-components-links"' }>
                            <li class="link">
                                <a href="components/ActivityComponent.html" data-type="entity-link" >ActivityComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/AddBankStep1Component.html" data-type="entity-link" >AddBankStep1Component</a>
                            </li>
                            <li class="link">
                                <a href="components/AddBankStep2Component.html" data-type="entity-link" >AddBankStep2Component</a>
                            </li>
                            <li class="link">
                                <a href="components/AddBankStep3Component.html" data-type="entity-link" >AddBankStep3Component</a>
                            </li>
                            <li class="link">
                                <a href="components/AppComponent.html" data-type="entity-link" >AppComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/BackOfficeActivityComponent.html" data-type="entity-link" >BackOfficeActivityComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/BanksDetailsComponent.html" data-type="entity-link" >BanksDetailsComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/BanksListComponent.html" data-type="entity-link" >BanksListComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/ConfirmDialogComponent.html" data-type="entity-link" >ConfirmDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/DashboardsListComponent.html" data-type="entity-link" >DashboardsListComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/EditBankComponent.html" data-type="entity-link" >EditBankComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/HomeScreenComponent.html" data-type="entity-link" >HomeScreenComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/LoadingDialogComponent.html" data-type="entity-link" >LoadingDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/LoginComponent.html" data-type="entity-link" >LoginComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SelectLimitsDialogComponent.html" data-type="entity-link" >SelectLimitsDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SideBarTestComponent.html" data-type="entity-link" >SideBarTestComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/SuccessDialogComponent.html" data-type="entity-link" >SuccessDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/TextDialogComponent.html" data-type="entity-link" >TextDialogComponent</a>
                            </li>
                            <li class="link">
                                <a href="components/TraceBatchModalComponent.html" data-type="entity-link" >TraceBatchModalComponent</a>
                            </li>
                        </ul>
                    </li>
                        <li class="chapter">
                            <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#directives-links"' :
                                'data-bs-target="#xs-directives-links"' }>
                                <span class="icon ion-md-code-working"></span>
                                <span>Directives</span>
                                <span class="icon ion-ios-arrow-down"></span>
                            </div>
                            <ul class="links collapse " ${ isNormalMode ? 'id="directives-links"' : 'id="xs-directives-links"' }>
                                <li class="link">
                                    <a href="directives/TrancheRangeValidatorDirective.html" data-type="entity-link" >TrancheRangeValidatorDirective</a>
                                </li>
                            </ul>
                        </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#classes-links"' :
                            'data-bs-target="#xs-classes-links"' }>
                            <span class="icon ion-ios-paper"></span>
                            <span>Classes</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="classes-links"' : 'id="xs-classes-links"' }>
                            <li class="link">
                                <a href="classes/BankReq.html" data-type="entity-link" >BankReq</a>
                            </li>
                            <li class="link">
                                <a href="classes/BankRes.html" data-type="entity-link" >BankRes</a>
                            </li>
                            <li class="link">
                                <a href="classes/CardProduct.html" data-type="entity-link" >CardProduct</a>
                            </li>
                            <li class="link">
                                <a href="classes/ErrorRes.html" data-type="entity-link" >ErrorRes</a>
                            </li>
                            <li class="link">
                                <a href="classes/LoginReq.html" data-type="entity-link" >LoginReq</a>
                            </li>
                            <li class="link">
                                <a href="classes/LoginRes.html" data-type="entity-link" >LoginRes</a>
                            </li>
                            <li class="link">
                                <a href="classes/MigBinRangePlasticProdModule.html" data-type="entity-link" >MigBinRangePlasticProdModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/MigLimitStandModule.html" data-type="entity-link" >MigLimitStandModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/MigResourcesModule.html" data-type="entity-link" >MigResourcesModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/MigServiceProdModule.html" data-type="entity-link" >MigServiceProdModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/NewBranchModule.html" data-type="entity-link" >NewBranchModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/PreMigCardFeesModule.html" data-type="entity-link" >PreMigCardFeesModule</a>
                            </li>
                            <li class="link">
                                <a href="classes/User.html" data-type="entity-link" >User</a>
                            </li>
                        </ul>
                    </li>
                        <li class="chapter">
                            <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#injectables-links"' :
                                'data-bs-target="#xs-injectables-links"' }>
                                <span class="icon ion-md-arrow-round-down"></span>
                                <span>Injectables</span>
                                <span class="icon ion-ios-arrow-down"></span>
                            </div>
                            <ul class="links collapse " ${ isNormalMode ? 'id="injectables-links"' : 'id="xs-injectables-links"' }>
                                <li class="link">
                                    <a href="injectables/AuthService.html" data-type="entity-link" >AuthService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/BankApiService.html" data-type="entity-link" >BankApiService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/BankService.html" data-type="entity-link" >BankService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/CampagneTestService.html" data-type="entity-link" >CampagneTestService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/DashboardService.html" data-type="entity-link" >DashboardService</a>
                                </li>
                                <li class="link">
                                    <a href="injectables/PatchArchetService.html" data-type="entity-link" >PatchArchetService</a>
                                </li>
                            </ul>
                        </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#interfaces-links"' :
                            'data-bs-target="#xs-interfaces-links"' }>
                            <span class="icon ion-md-information-circle-outline"></span>
                            <span>Interfaces</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? ' id="interfaces-links"' : 'id="xs-interfaces-links"' }>
                            <li class="link">
                                <a href="interfaces/Architecte.html" data-type="entity-link" >Architecte</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/BankWithUI.html" data-type="entity-link" >BankWithUI</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Batch.html" data-type="entity-link" >Batch</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/BatchResult.html" data-type="entity-link" >BatchResult</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Campagne.html" data-type="entity-link" >Campagne</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Campaign.html" data-type="entity-link" >Campaign</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/ConfirmDialogData.html" data-type="entity-link" >ConfirmDialogData</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/ContextBank.html" data-type="entity-link" >ContextBank</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Country.html" data-type="entity-link" >Country</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Currency.html" data-type="entity-link" >Currency</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/LanguageOption.html" data-type="entity-link" >LanguageOption</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/LoadingDialogData.html" data-type="entity-link" >LoadingDialogData</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Patch.html" data-type="entity-link" >Patch</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/RapportResult.html" data-type="entity-link" >RapportResult</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Resource.html" data-type="entity-link" >Resource</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/SimulationResult.html" data-type="entity-link" >SimulationResult</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/StepInfo.html" data-type="entity-link" >StepInfo</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/SuccessDialogData.html" data-type="entity-link" >SuccessDialogData</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/TraceBatchModel.html" data-type="entity-link" >TraceBatchModel</a>
                            </li>
                            <li class="link">
                                <a href="interfaces/Transaction.html" data-type="entity-link" >Transaction</a>
                            </li>
                        </ul>
                    </li>
                    <li class="chapter">
                        <div class="simple menu-toggler" data-bs-toggle="collapse" ${ isNormalMode ? 'data-bs-target="#miscellaneous-links"'
                            : 'data-bs-target="#xs-miscellaneous-links"' }>
                            <span class="icon ion-ios-cube"></span>
                            <span>Miscellaneous</span>
                            <span class="icon ion-ios-arrow-down"></span>
                        </div>
                        <ul class="links collapse " ${ isNormalMode ? 'id="miscellaneous-links"' : 'id="xs-miscellaneous-links"' }>
                            <li class="link">
                                <a href="miscellaneous/functions.html" data-type="entity-link">Functions</a>
                            </li>
                            <li class="link">
                                <a href="miscellaneous/variables.html" data-type="entity-link">Variables</a>
                            </li>
                        </ul>
                    </li>
                    <li class="chapter">
                        <a data-type="chapter-link" href="coverage.html"><span class="icon ion-ios-stats"></span>Documentation coverage</a>
                    </li>
                    <li class="divider"></li>
                    <li class="copyright">
                        Documentation generated using <a href="https://compodoc.app/" target="_blank" rel="noopener noreferrer">
                            <img data-src="images/compodoc-vectorise-inverted.png" class="img-responsive" data-type="compodoc-logo">
                        </a>
                    </li>
            </ul>
        </nav>
        `);
        this.innerHTML = tp.strings;
    }
});