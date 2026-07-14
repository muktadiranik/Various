import { chromium, FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

import { ENV, STORAGE } from '../src/constants';
import { LoginPage } from '../src/pages/login.page';

async function globalSetup(config: FullConfig): Promise<void> {
  const browser = await chromium.launch({
    headless: true,
  });

  const context = await browser.newContext({
    baseURL: config.projects[0].use.baseURL as string,
  });

  const page = await context.newPage();

  const loginPage = new LoginPage(page);

  const storageDir = path.dirname(STORAGE.AUTH);

  if (!fs.existsSync(storageDir)) {
    fs.mkdirSync(storageDir, {
      recursive: true,
    });
  }

  await loginPage.open();

  await loginPage.login(
    ENV.EMAIL,
    ENV.PASSWORD
  );

  await loginPage.expectLoginSuccess();

  await context.storageState({
    path: STORAGE.AUTH,
  });

  await browser.close();
}

export default globalSetup;