import { APIRequestContext, APIResponse, request } from "@playwright/test";

import { API_ROUTES, ENV } from "../constants";

import { ArticleData } from "../utils/random-data";

interface LoginResponse {
  user: {
    email: string;
    token: string;
    username: string;
    bio: string;
    image: string;
  };
}

interface ArticleResponse {
  article: {
    slug: string;
    title: string;
    description: string;
    body: string;
    tagList: string[];
  };
}

export class ApiClient {
  private apiContext!: APIRequestContext;

  private token = "";

  /**
   * Initialize API client.
   */
  async init(): Promise<void> {
    this.apiContext = await request.newContext({
      baseURL: `${ENV.API_URL}/`,
      extraHTTPHeaders: {
        "Content-Type": "application/json",
      },
    });
  }

  /**
   * Login user and store JWT token.
   */
  async login(): Promise<string> {
    const response = await this.apiContext.post(API_ROUTES.LOGIN, {
      data: {
        user: {
          email: ENV.EMAIL,
          password: ENV.PASSWORD,
        },
      },
    });

    await this.ensureSuccess(response);

    const body = (await response.json()) as LoginResponse;

    this.token = body.user.token;

    return this.token;
  }

  /**
   * Create article through API.
   */
  async createArticle(article: ArticleData): Promise<ArticleResponse["article"]> {
    const response = await this.apiContext.post(API_ROUTES.ARTICLES, {
      headers: {
        Authorization: `Token ${this.token}`,
      },

      data: {
        article: {
          title: article.title,
          description: article.description,
          body: article.body,
          tagList: article.tags,
        },
      },
    });

    await this.ensureSuccess(response);

    const body = (await response.json()) as ArticleResponse;

    return body.article;
  }

  /**
   * Delete article through API.
   */
  async deleteArticle(slug: string): Promise<void> {
    const response = await this.apiContext.delete(`${API_ROUTES.ARTICLES}/${slug}`, {
      headers: {
        Authorization: `Token ${this.token}`,
      },
    });

    await this.ensureSuccess(response);
  }

  /**
   * Update article through API.
   */
  async updateArticle(slug: string, article: Partial<ArticleData>): Promise<ArticleResponse["article"]> {
    const response = await this.apiContext.put(`${API_ROUTES.ARTICLES}/${slug}`, {
      headers: {
        Authorization: `Token ${this.token}`,
      },

      data: {
        article,
      },
    });

    await this.ensureSuccess(response);

    const body = (await response.json()) as ArticleResponse;

    return body.article;
  }

  /**
   * Validate API response.
   */
  private async ensureSuccess(response: APIResponse): Promise<void> {
    if (!response.ok()) {
      const body = await response.text();

      throw new Error(`API request failed\n` + `Status: ${response.status()}\n` + `URL: ${response.url()}\n` + `Response: ${body}`);
    }
  }

  /**
   * Dispose API context.
   */
  async dispose(): Promise<void> {
    if (this.apiContext) {
      await this.apiContext.dispose();
    }
  }
}
