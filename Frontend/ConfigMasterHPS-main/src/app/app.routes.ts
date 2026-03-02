import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { HomeScreenComponent } from './home-screen/home-screen.component';
import { DashboardsListComponent } from './dashboards-list/dashboards-list.component';
import { BanksListComponent } from './banks-list/banks-list.component';
import { ActivityComponent } from './activity/activity.component';
import { AddBankStep1Component } from './add-bank-step1/add-bank-step1.component';
import { AddBankStep2Component } from './add-bank-step2/add-bank-step2.component';
import { AddBankStep3Component } from './add-bank-step3/add-bank-step3.component';
import { BanksDetailsComponent } from './banks-details/banks-details.component';
import { SideBarTestComponent } from './side-bar-test/side-bar-test.component';
import { EditBankComponent } from './edit-bank/edit-bank.component';
import { RenderMode } from '@angular/ssr';
import { BackOfficeActivityComponent } from './back-office-activity/back-office-activity.component';
import { AiAgentComponent } from './ai-agent/ai-agent.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'home', component: HomeScreenComponent },
  { path: 'dashboards', component: DashboardsListComponent },
  { path: 'banks', component: BanksListComponent },
  {
    path: 'banks/details/:codeBank',
    component: BanksDetailsComponent,
    data: { RenderMode: RenderMode.Client },
  },
  {
    path: 'banks/edit/:bankCode',
    component: EditBankComponent,
    data: { RenderMode: RenderMode.Client },
  },
  { path: 'activity', component: ActivityComponent },
  { path: 'addbank/step1', component: AddBankStep1Component },
  { path: 'addbank/step2', component: AddBankStep2Component },
  { path: 'addbank/step3', component: AddBankStep3Component },
  { path: 'side-bar-test', component: SideBarTestComponent },
  {path:'backOfficeActivity',component:BackOfficeActivityComponent},
  { path: 'agent', component: AiAgentComponent },
  { path: '**', component: HomeScreenComponent }
];
