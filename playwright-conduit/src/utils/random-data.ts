import { faker } from '@faker-js/faker';

export interface ArticleData {
  title: string;
  description: string;
  body: string;
  tags: string[];
}

export interface UserSettingsData {
  username: string;
  image: string;
  bio: string;
  email: string;
  password: string;
}

const AVAILABLE_TAGS = [
  'playwright',
  'typescript',
  'automation',
  'testing',
  'qa',
  'e2e',
  'web',
  'javascript'
];

/**
 * Returns a unique article title.
 */
export function generateArticleTitle(): string {
  return `${faker.lorem.words(3)} ${Date.now()}`;
}

/**
 * Returns a short article description.
 */
export function generateArticleDescription(): string {
  return faker.lorem.sentence();
}

/**
 * Returns a multi-paragraph article body.
 */
export function generateArticleBody(): string {
  return faker.lorem.paragraphs();
}

/**
 * Returns between 1 and 3 random tags.
 */
export function generateTags(): string[] {
  return faker.helpers.arrayElements(
    AVAILABLE_TAGS,
    faker.number.int({ min: 1, max: 3 })
  );
}

/**
 * Returns a complete article object.
 */
export function generateArticle(): ArticleData {
  return {
    title: generateArticleTitle(),
    description: generateArticleDescription(),
    body: generateArticleBody(),
    tags: generateTags(),
  };
}

/**
 * Returns updated user settings.
 */
export function generateUserSettings(
  email: string,
  password: string
): UserSettingsData {
  const timestamp = Date.now();

  return {
    username: `playwright-${timestamp}`,
    image: `https://i.pravatar.cc/300?img=${Math.floor(
      Math.random() * 70
    )}`,
    bio: `Updated bio ${timestamp}`,
    email,
    password,
  };
}

/**
 * Returns an invalid email for negative tests.
 */
export function generateInvalidEmail(): string {
  return 'invalid-email';
}

/**
 * Returns an empty article.
 */
export function generateEmptyArticle(): ArticleData {
  return {
    title: '',
    description: '',
    body: '',
    tags: [],
  };
}

/**
 * Returns a very long string for boundary testing.
 */
export function generateLongText(length = 5000): string {
  return faker.string.alphanumeric(length);
}

/**
 * Returns a random tag.
 */
export function generateRandomTag(): string {
  return faker.helpers.arrayElement(AVAILABLE_TAGS);
}