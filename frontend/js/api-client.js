/**
 * API Client for Email Service
 * Handles all API communication with the FastAPI backend
 */

class EmailAPIClient {
  constructor(apiBaseUrl = "http://localhost:8000/email") {
    this.apiBaseUrl = apiBaseUrl;
    this.accessToken = null;
    this.provider = null;
  }

  setCredentials(provider, accessToken) {
    this.provider = provider;
    this.accessToken = accessToken;
  }

  async request(endpoint, method = "POST", data = {}) {
    const url = `${this.apiBaseUrl}${endpoint}`;
    
    const payload = {
      provider: this.provider,
      access_token: this.accessToken,
      ...data
    };

    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        // Handle 401 Unauthorized - redirect to login
        if (response.status === 401) {
          console.warn("Unauthorized access - redirecting to login");
          sessionStorage.removeItem("email_provider");
          sessionStorage.removeItem("email_token");
          setTimeout(() => {
            window.location.href = "index.html";
          }, 500);
          return;
        }

        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error (${endpoint}):`, error);
      throw error;
    }
  }

  /**
   * Check if access token is valid
   */
  async checkHealth() {
    return this.request("/health");
  }

  /**
   * Get list of all folders
   */
  async getFolders() {
    const response = await this.request("/folders");
    return response.folders || [];
  }

  /**
   * Get emails from a specific folder
   * @param {Object} options - Query options
   * @param {string} options.folder - Folder name (e.g., 'INBOX', 'SENT')
   * @param {number} options.page_size - Number of emails to fetch (default: 10)
   * @param {string} options.cursor - Pagination cursor
   * @param {Object} options.filters - Email search filters
   */
  async getInbox(options = {}) {
    const data = {
      page_size: options.page_size || 20,
      cursor: options.cursor || null,
    };

    // Only include folder if specified; otherwise fetch from all labels
    if (options.folder) {
      data.folder = options.folder;
    }

    if (options.filters) {
      data.filters = options.filters;
    }

    return this.request("/inbox", "POST", data);
  }

  /**
   * Get detailed information about a specific email
   * @param {string} messageId - Email message ID
   */
  async getEmailDetail(messageId) {
    return this.request("/detail", "POST", {
      message_id: messageId
    });
  }

  /**
   * Get list of attachments for an email
   * @param {string} messageId - Email message ID
   */
  async getAttachments(messageId) {
    const response = await this.request("/attachments", "POST", {
      message_id: messageId
    });
    return response.attachments || [];
  }

  /**
   * Download a specific attachment
   * @param {string} messageId - Email message ID
   * @param {string} attachmentId - Attachment ID
   */
  async downloadAttachment(messageId, attachmentId) {
    const url = `${this.apiBaseUrl}/attachment/download`;
    
    const payload = {
      provider: this.provider,
      access_token: this.accessToken,
      message_id: messageId,
      attachment_id: attachmentId
    };

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}`);
      }

      // Get the JSON response containing base64-encoded content
      const data = await response.json();
      // Return base64 string (will be decoded by the caller)
      return data.content_base64;
    } catch (error) {
      console.error(`API Error (attachment/download):`, error);
      throw error;
    }
  }

  /**
   * Build advanced search filters
   * @param {Object} filterOptions - Filter options
   */
  static buildFilters(filterOptions = {}) {
    const filters = {};

    // Handle from_address
    if (filterOptions.from_address) filters.from_address = filterOptions.from_address;
    if (filterOptions.from) filters.from_address = filterOptions.from;

    // Handle to_addresses
    if (filterOptions.to_addresses) {
      filters.to_addresses = Array.isArray(filterOptions.to_addresses)
        ? filterOptions.to_addresses
        : [filterOptions.to_addresses];
    }
    if (filterOptions.to) filters.to_addresses = [filterOptions.to];

    // Handle subject
    if (filterOptions.subject_contains) filters.subject_contains = filterOptions.subject_contains;
    if (filterOptions.subject) filters.subject_contains = filterOptions.subject;

    // Handle body
    if (filterOptions.body_contains) filters.body_contains = filterOptions.body_contains;
    if (filterOptions.body) filters.body_contains = filterOptions.body;

    // Handle attachments
    if (filterOptions.has_attachments !== undefined && filterOptions.has_attachments !== null) {
      filters.has_attachments = filterOptions.has_attachments;
    }

    // Handle read status
    if (filterOptions.is_read !== undefined && filterOptions.is_read !== null) {
      filters.is_read = filterOptions.is_read;
    }

    // Handle dates
    if (filterOptions.start_date) filters.start_date = filterOptions.start_date;
    if (filterOptions.startDate) filters.start_date = filterOptions.startDate;
    
    if (filterOptions.end_date) filters.end_date = filterOptions.end_date;
    if (filterOptions.endDate) filters.end_date = filterOptions.endDate;

    // Handle keywords/has_words
    if (filterOptions.has_words) {
      filters.has_words = Array.isArray(filterOptions.has_words)
        ? filterOptions.has_words
        : [filterOptions.has_words];
    }
    if (filterOptions.keywords) filters.has_words = filterOptions.keywords;

    return Object.keys(filters).length > 0 ? filters : null;
  }

  /**
   * Parse search query string
   * Supports Google/Gmail style search syntax
   * Examples:
   *   "invoice" -> search in subject and body
   *   "from:john@example.com" -> filter by sender
   *   "to:team@example.com" -> filter by recipient
   *   "has:attachment" -> only emails with attachments
   *   "is:unread" -> only unread emails
   *   "before:2024-01-01" -> emails before date
   *   "after:2024-01-01" -> emails after date
   */
  static parseSearchQuery(query) {
    const filters = {};
    const parts = query.split(/\s+/);
    const keywords = [];

    for (const part of parts) {
      if (part.startsWith("from:")) {
        filters.from = part.substring(5);
      } else if (part.startsWith("to:")) {
        filters.to = part.substring(3);
      } else if (part.startsWith("subject:")) {
        filters.subject = part.substring(8);
      } else if (part === "has:attachment") {
        filters.has_attachments = true;
      } else if (part === "is:unread") {
        filters.is_read = false;
      } else if (part === "is:read") {
        filters.is_read = true;
      } else if (part.startsWith("before:")) {
        filters.endDate = part.substring(7) + "T23:59:59";
      } else if (part.startsWith("after:")) {
        filters.startDate = part.substring(6) + "T00:00:00";
      } else if (!part.startsWith("-")) {
        keywords.push(part);
      }
    }

    if (keywords.length > 0) {
      filters.keywords = keywords;
    }

    return filters;
  }
}

// Create global API client instance
const apiClient = new EmailAPIClient();
