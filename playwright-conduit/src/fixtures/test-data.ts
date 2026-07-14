import { ENV } from '@constants/index';
import {
  ArticleData,
  UserSettingsData,
  generateArticle,
  generateEmptyArticle,
  generateInvalidEmail,
  generateLongText,
  generateRandomTag,
  generateUserSettings,
} from '@utils/random-data';

export interface Credentials {
  email: string;
  password: string;
}

export const testUser: Credentials = {
  email: ENV.EMAIL,
  password: ENV.PASSWORD,
};

/**
 * Returns a brand-new valid article.
 * Every call generates unique data.
 */
export function validArticle(): ArticleData {
  return generateArticle();
}

/**
 * Invalid article used for negative tests.
 */
export function invalidArticle(): ArticleData {
  return generateEmptyArticle();
}

/**
 * Article containing extremely long values.
 */
export function boundaryArticle(): ArticleData {
  return {
    title: generateLongText(255),
    description: generateLongText(500),
    body: generateLongText(5000),
    tags: [generateRandomTag()],
  };
}

/**
 * Valid settings payload.
 */
export function validUserSettings(): UserSettingsData {
  return generateUserSettings(
    testUser.email,
    testUser.password
  );
}

/**
 * Invalid settings payload.
 */
export function invalidUserSettings(): UserSettingsData {
  return {
    image: '',
    bio: '',
    email: generateInvalidEmail(),
    password: testUser.password,
  };
}

/**
 * Common tags used in filter tests.
 */
export const TAGS = {
  PLAYWRIGHT: 'playwright',
  TYPESCRIPT: 'typescript',
  AUTOMATION: 'automation',
  TESTING: 'testing',
};

/**
 * Frequently used validation messages.
 * Keeping them in one place makes maintenance easier.
 */
export const MESSAGES = {
  ARTICLE_PUBLISHED: 'Article Published',
  ARTICLE_UPDATED: 'Article Updated',
  SETTINGS_UPDATED: 'Settings updated',
  INVALID_LOGIN: 'email or password is invalid',
  REQUIRED_FIELD: 'required',
};

/**
 * Timeouts used by some tests.
 */
export const WAIT = {
  SHORT: 2_000,
  MEDIUM: 5_000,
  LONG: 10_000,
};