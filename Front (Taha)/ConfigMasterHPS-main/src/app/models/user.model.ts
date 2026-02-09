// user.model.ts
export class LoginReq {
  constructor(public email: string, public password: string) {}
}

export class LoginRes {
  constructor(public email: string, public token: string) {}
}

export class User {
  email!: string;
  password?: string;
  firstName?: string;
  lastName?: string;
}
