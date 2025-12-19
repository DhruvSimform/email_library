/**
 * Email Client - Main Application Logic
 * Handles UI interactions and state management
 */

class EmailClientApp {
  constructor() {
    this.currentProvider = null;
    this.currentAccessToken = null;
    this.currentFolder = null;
    this.currentEmailId = null;
    this.emails = [];
    this.nextCursor = null;
    this.folders = [];

    this.initializeElements();
    this.attachEventListeners();
    this.loadStoredCredentials();
  }

  initializeElements() {
    // Header elements
    this.providerSelector = document.getElementById("providerSelector");
    this.searchInput = document.getElementById("searchInput");
    this.logoutBtn = document.getElementById("logoutBtn");
    this.filterToggleBtn = document.getElementById("filterToggleBtn");

    // Sidebar elements
    this.folderList = document.getElementById("folderList");

    // Main content elements
    this.emailListContainer = document.getElementById("emailListContainer");
    this.emailDetailContainer = document.getElementById("emailDetailContainer");

    // Email detail elements
    this.detailSubject = document.getElementById("detailSubject");
    this.detailFrom = document.getElementById("detailFrom");
    this.detailDate = document.getElementById("detailDate");
    this.detailBody = document.getElementById("detailBody");
    this.attachmentsSection = document.getElementById("attachmentsSection");
    this.attachmentsList = document.getElementById("attachmentsList");

    // Action buttons
    this.backBtn = document.getElementById("backBtn");
    this.replyBtn = document.getElementById("replyBtn");
    this.deleteBtn = document.getElementById("deleteBtn");

    // Filter panel elements
    this.filterPanel = document.getElementById("filterPanel");
    this.filterPanelOverlay = document.getElementById("filterPanelOverlay");
    this.filterCloseBtn = document.getElementById("filterCloseBtn");
    this.filterApplyBtn = document.getElementById("filterApplyBtn");
    this.filterClearBtn = document.getElementById("filterClearBtn");
  }

  attachEventListeners() {
    this.providerSelector.addEventListener("change", (e) => this.onProviderChange(e));
    this.searchInput.addEventListener("keyup", (e) => this.onSearch(e));
    this.logoutBtn.addEventListener("click", () => this.logout());
    this.backBtn.addEventListener("click", () => this.showEmailList());
    this.replyBtn.addEventListener("click", () => this.onReply());
    this.deleteBtn.addEventListener("click", () => this.onDelete());
    
    // Filter panel listeners
    this.filterToggleBtn.addEventListener("click", () => this.openFilterPanel());
    this.filterCloseBtn.addEventListener("click", () => this.closeFilterPanel());
    this.filterPanelOverlay.addEventListener("click", () => this.closeFilterPanel());
    this.filterApplyBtn.addEventListener("click", () => this.applyFilters());
    this.filterClearBtn.addEventListener("click", () => this.clearFilters());
  }

  loadStoredCredentials() {
    // Try to load stored credentials from sessionStorage or localStorage
    const stored = {
      provider: sessionStorage.getItem("email_provider"),
      token: sessionStorage.getItem("email_token")
    };

    if (stored.provider && stored.token) {
      this.currentProvider = stored.provider;
      this.currentAccessToken = stored.token;
      this.setupClient();
    }
  }

  async onProviderChange(event) {
    const provider = event.target.value;

    if (!provider) {
      this.logout();
      return;
    }

    // Prompt user to paste access token
    const token = prompt(`Paste your ${provider.toUpperCase()} access token:`);
    if (!token) {
      this.providerSelector.value = "";
      return;
    }

    this.currentProvider = provider;
    this.currentAccessToken = token;

    // Store in session
    sessionStorage.setItem("email_provider", provider);
    sessionStorage.setItem("email_token", token);

    this.setupClient();
  }

  setupClient() {
    apiClient.setCredentials(this.currentProvider, this.currentAccessToken);
    this.logoutBtn.style.display = "block";
    this.providerSelector.value = this.currentProvider;

    // Load folders
    this.loadFolders();
  }

  logout() {
    this.currentProvider = null;
    this.currentAccessToken = null;
    this.currentFolder = null;
    this.emails = [];

    sessionStorage.removeItem("email_provider");
    sessionStorage.removeItem("email_token");

    this.providerSelector.value = "";
    this.logoutBtn.style.display = "none";
    this.folderList.innerHTML = `
      <div class="empty-state">
        <div style="font-size: 14px;">Select a provider to get started</div>
      </div>
    `;
    this.showEmptyEmailList();
    this.showEmptyEmailDetail();
  }

  async loadFolders() {
    try {
      this.setFolderLoading(true);
      const folders = await apiClient.getFolders();
      this.folders = folders;
      this.renderFolders(folders);
    } catch (error) {
      this.showError("Failed to load folders", error);
    } finally {
      this.setFolderLoading(false);
    }
  }

  setFolderLoading(loading) {
    if (loading) {
      this.folderList.innerHTML = `
        <div class="folder-item">
          <div class="spinner" style="width: 16px; height: 16px; border-width: 2px;"></div>
        </div>
      `;
    }
  }

  renderFolders(folders) {
    // Create folder items with "All Labels" as first item
    const allLabelsItem = `
      <div class="folder-item ${!this.currentFolder ? "active" : ""}" data-folder="all">
        <i class="fas fa-inbox folder-icon"></i>
        <span>All Labels</span>
        <span class="folder-unread">0</span>
      </div>
    `;

    const folderItems = folders.map((folder) => `
      <div class="folder-item ${this.currentFolder === folder ? "active" : ""}" data-folder="${folder}">
        <i class="fas fa-folder folder-icon"></i>
        <span>${this.humanizeFolder(folder)}</span>
        <span class="folder-unread">0</span>
      </div>
    `).join("");

    this.folderList.innerHTML = allLabelsItem + folderItems;

    // Add event listeners
    this.folderList.querySelectorAll(".folder-item").forEach((item) => {
      item.addEventListener("click", () => this.onFolderSelect(item));
    });

    // Select "All Labels" by default if no folder selected
    if (!this.currentFolder) {
      this.folderList.querySelector(".folder-item[data-folder='all']").click();
    }
  }

  humanizeFolder(folder) {
    const folderMap = {
      "INBOX": "Inbox",
      "SENT": "Sent",
      "DRAFTS": "Drafts",
      "TRASH": "Trash",
      "SPAM": "Spam",
      "STARRED": "Starred",
      "IMPORTANT": "Important",
      "ARCHIVE": "Archive",
      "ALLMAIL": "All Mail"
    };
    return folderMap[folder] || folder;
  }

  async onFolderSelect(element) {
    const folder = element.dataset.folder;
    
    // If "All Labels" is selected, set currentFolder to null
    this.currentFolder = folder === "all" ? null : folder;

    // Update active folder
    this.folderList.querySelectorAll(".folder-item").forEach((item) => {
      item.classList.remove("active");
    });
    element.classList.add("active");

    // Load emails
    this.loadEmails();
  }

  async loadEmails(cursor = null, filters = null) {
    try {
      this.showEmailListLoading();

      const options = {
        page_size: 20,
        cursor: cursor
      };

      // Only include folder if currentFolder is not null
      if (this.currentFolder) {
        options.folder = this.currentFolder;
      }

      if (filters) {
        options.filters = EmailAPIClient.buildFilters(filters);
      }

      const response = await apiClient.getInbox(options);
      this.emails = response.emails || [];
      this.nextCursor = response.next_cursor;

      this.renderEmailList(this.emails);
    } catch (error) {
      this.showError("Failed to load emails", error);
      this.emailListContainer.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon"><i class="fas fa-exclamation-circle"></i></div>
          <div>${error.message}</div>
        </div>
      `;
    }
  }

  renderEmailList(emails) {
    if (emails.length === 0) {
      this.showEmptyEmailList();
      return;
    }

    this.emailListContainer.innerHTML = emails.map((email) => {
      const { name, email: emailAddr } = this.parseSender(email.sender || "");
      const avatarColor = this.getAvatarColor(emailAddr);
      const initials = this.getInitials(emailAddr);
      
      // Build inbox classification badge (only when no folder is selected)
      let classificationBadge = "";
      if (!this.currentFolder && email.inbox_classification) {
        const classification = email.inbox_classification.toLowerCase();
        const badgeText = classification.charAt(0).toUpperCase() + classification.slice(1);
        classificationBadge = `<span class="inbox-classification-badge inbox-classification-${classification}" title="${classification}">${badgeText}</span>`;
      }
      
      // Build attachment section (show max 3 items + counter)
      let attachmentSection = "";
      if (email.has_attachments && email.attachments && email.attachments.length > 0) {
        const maxDisplayAttachments = 3;
        const displayAttachments = email.attachments.slice(0, maxDisplayAttachments);
        const remainingCount = email.attachments.length - maxDisplayAttachments;
        
        const attachmentItems = displayAttachments.map((att) => {
          const fileIcon = this.getFileIcon(att.mime_type);
          const fileExt = att.filename.split('.').pop().toUpperCase().slice(0, 3);
          return `
            <div class="list-attachment-item">
              <i class="fas ${fileIcon} attachment-type-icon"></i>
              <span class="list-attachment-name" title="${att.filename}">${att.filename}</span>
              <span class="list-attachment-size">${this.formatBytes(att.size_bytes)}</span>
            </div>
          `;
        }).join("");
        
        let moreAttachmentsText = "";
        if (remainingCount > 0) {
          moreAttachmentsText = `<div class="list-attachment-item attachment-more">+${remainingCount} more</div>`;
        }
        
        attachmentSection = `
          <div class="email-attachments-preview">
            ${attachmentItems}${moreAttachmentsText}
          </div>
        `;
      }
      
      return `
      <div class="email-item ${this.currentEmailId === email.message_id ? "active" : ""}" 
           data-email-id="${email.message_id}">
        <div class="email-avatar" style="background: linear-gradient(135deg, ${avatarColor} 0%, ${this.shadeColor(avatarColor, -20)} 100%);" title="${emailAddr}">${initials}</div>
        <div class="email-preview">
          <div class="email-header-row">
            <div class="email-from ${email.is_read ? "" : "email-unread"}">${name}</div>
            <div class="email-date">${this.formatDate(email.timestamp)}</div>
          </div>
          <div class="email-subject ${email.is_read ? "" : "email-unread"}">
            <span class="email-subject-text">${email.subject}</span>
            ${email.has_attachments ? `<span class="attachment-badge-inline" title="${email.attachment_count} attachment(s)"><i class="fas fa-paperclip"></i></span>` : ""}
            ${classificationBadge}
          </div>
          <div class="email-snippet">${this.truncate(email.preview, 60)}</div>
          ${attachmentSection}
        </div>
      </div>
    `;
    }).join("");

    // Add event listeners
    this.emailListContainer.querySelectorAll(".email-item").forEach((item) => {
      item.addEventListener("click", () => this.onEmailSelect(item));
    });
  }  showEmptyEmailList() {
    this.emailListContainer.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon"><i class="fas fa-inbox"></i></div>
        <div>No emails found</div>
      </div>
    `;
  }

  showEmailListLoading() {
    this.emailListContainer.innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
        <div style="margin-top: 16px;">Loading emails...</div>
      </div>
    `;
  }

  async onEmailSelect(element) {
    const emailId = element.dataset.emailId;
    const email = this.emails.find((e) => e.message_id === emailId);

    if (!email) return;

    this.currentEmailId = emailId;

    // Update active email
    this.emailListContainer.querySelectorAll(".email-item").forEach((item) => {
      item.classList.remove("active");
    });
    element.classList.add("active");

    // Load and show email detail
    this.loadEmailDetail(emailId, email);
  }

  async loadEmailDetail(emailId, preview) {
    try {
      this.showEmailDetailLoading();
      const detail = await apiClient.getEmailDetail(emailId);
      this.renderEmailDetail(detail);
    } catch (error) {
      this.detailBody.innerHTML = `
        <div style="color: #dc3545; padding: 20px;">
          Failed to load email: ${error.message}
        </div>
      `;
    }
  }

  renderEmailDetail(email) {
    // Show detail container
    this.emailDetailContainer.style.display = "flex";

    // Parse sender to get name
    const { name, email: emailAddr } = this.parseSender(email.sender || "");
    const avatarColor = this.getAvatarColor(emailAddr);
    const initials = this.getInitials(emailAddr);

    // Update header with avatar
    const detailFromAvatar = document.getElementById("detailFromAvatar");
    detailFromAvatar.textContent = initials;
    detailFromAvatar.style.background = `linear-gradient(135deg, ${avatarColor} 0%, ${this.shadeColor(avatarColor, -20)} 100%)`;
    detailFromAvatar.title = emailAddr;

    // Update text fields
    this.detailSubject.textContent = email.subject;
    this.detailFrom.textContent = name;
    
    const detailFromEmail = document.getElementById("detailFromEmail");
    detailFromEmail.textContent = emailAddr;
    
    this.detailDate.textContent = this.formatDateLong(email.timestamp);

    // Render recipients, CC, and BCC
    this.renderRecipients(email.recipients);
    this.renderCc(email.cc);
    this.renderBcc(email.bcc);

    // Update body - prefer HTML body, fall back to text
    const bodyContent = email.body_html || email.body_text || "No content available";
    this.detailBody.innerHTML = `<div class="email-body">${this.sanitizeHtml(bodyContent)}</div>`;

    // Load and show attachments
    if (email.attachments && email.attachments.length > 0) {
      this.renderAttachments(email.attachments, email.message_id);
    } else {
      this.attachmentsSection.style.display = "none";
    }
  }

  renderRecipients(recipients) {
    const recipientsList = document.getElementById("recipientsList");
    if (!recipients || recipients.length === 0) {
      recipientsList.innerHTML = '<div style="color: #999; font-size: 12px;">No recipients</div>';
      return;
    }

    recipientsList.innerHTML = recipients
      .map((recipient) => `<div class="recipient-badge">${recipient}</div>`)
      .join("");
  }

  renderCc(cc) {
    const ccContainer = document.getElementById("detailCc");
    const ccList = document.getElementById("ccList");
    
    if (!cc || cc.length === 0) {
      ccContainer.style.display = "none";
      return;
    }

    ccContainer.style.display = "block";
    ccList.innerHTML = cc
      .map((email) => `<div class="recipient-badge">${email}</div>`)
      .join("");
  }

  renderBcc(bcc) {
    const bccContainer = document.getElementById("detailBcc");
    const bccList = document.getElementById("bccList");
    
    if (!bcc || bcc.length === 0) {
      bccContainer.style.display = "none";
      return;
    }

    bccContainer.style.display = "block";
    bccList.innerHTML = bcc
      .map((email) => `<div class="recipient-badge">${email}</div>`)
      .join("");
  }

  showEmailDetailLoading() {
    this.emailDetailContainer.style.display = "flex";
    this.detailSubject.textContent = "Loading...";
    this.detailFrom.textContent = "-";
    this.detailDate.textContent = "-";
    this.detailBody.innerHTML = `
      <div class="loading">
        <div class="spinner"></div>
      </div>
    `;
    this.attachmentsSection.style.display = "none";
  }

  showEmptyEmailDetail() {
    this.emailDetailContainer.style.display = "none";
  }

  getFileIcon(mimeType) {
    if (!mimeType) return "fa-file";
    if (mimeType.startsWith("image/")) return "fa-image";
    if (mimeType.startsWith("video/")) return "fa-video";
    if (mimeType.startsWith("audio/")) return "fa-music";
    if (mimeType.includes("pdf")) return "fa-file-pdf";
    if (mimeType.includes("word")) return "fa-file-word";
    if (mimeType.includes("excel") || mimeType.includes("spreadsheet")) return "fa-file-excel";
    if (mimeType.includes("powerpoint") || mimeType.includes("presentation")) return "fa-file-powerpoint";
    if (mimeType.includes("zip") || mimeType.includes("archive")) return "fa-file-archive";
    return "fa-file";
  }

  renderAttachments(attachments, emailId) {
    if (!attachments || attachments.length === 0) {
      this.attachmentsSection.style.display = "none";
      return;
    }

    this.attachmentsList.innerHTML = attachments.map((att) => {
      const fileIcon = this.getFileIcon(att.mime_type);
      const fileExtension = att.filename.split('.').pop().toUpperCase().slice(0, 3);
      
      return `
      <div class="attachment-item-gmail">
        <div class="attachment-icon-wrapper">
          <i class="fas ${fileIcon} attachment-file-icon"></i>
          <span class="attachment-ext">${fileExtension}</span>
        </div>
        <div class="attachment-info">
          <div class="attachment-filename" title="${att.filename}">${att.filename}</div>
          <div class="attachment-size">${this.formatBytes(att.size_bytes)}</div>
        </div>
        <button class="attachment-btn-download" 
           data-message-id="${emailId}" 
           data-attachment-id="${att.attachment_id}"
           data-mime-type="${att.mime_type}"
           title="Download ${att.filename}">
          <i class="fas fa-download"></i>
        </button>
      </div>
    `;
    }).join("");

    this.attachmentsSection.style.display = "block";

    // Add download listeners
    this.attachmentsList.querySelectorAll(".attachment-btn-download").forEach((btn) => {
      btn.addEventListener("click", () => this.onDownloadAttachment(btn));
    });
  }

  async loadAttachments(emailId) {
    try {
      const attachments = await apiClient.getAttachments(emailId);

      if (attachments.length === 0) {
        this.attachmentsSection.style.display = "none";
        return;
      }

      this.renderAttachments(attachments, emailId);
    } catch (error) {
      console.error("Failed to load attachments:", error);
      this.attachmentsSection.style.display = "none";
    }
  }

  async onDownloadAttachment(button) {
    const messageId = button.dataset.messageId;
    const attachmentId = button.dataset.attachmentId;
    const mimeType = button.dataset.mimeType;
    const filename = button.closest(".attachment-item-gmail").querySelector(".attachment-filename").textContent;

    const originalContent = button.innerHTML;
    button.innerHTML = '<div class="spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>';
    button.disabled = true;

    try {
      // Call the download API - returns base64-encoded content
      const base64Content = await apiClient.downloadAttachment(messageId, attachmentId);
      
      // Decode base64 to binary
      const binaryString = atob(base64Content);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Create a blob with the correct MIME type from attachment metadata
      const blob = new Blob([bytes.buffer], { type: mimeType || 'application/octet-stream' });
      
      // Create a temporary URL for the blob
      const blobUrl = window.URL.createObjectURL(blob);
      
      // Create a temporary anchor element to trigger download
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = filename || 'attachment';
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Clean up the blob URL
      window.URL.revokeObjectURL(blobUrl);
      
      // Show success message
      console.log(`Downloaded: ${filename}`);
      button.innerHTML = '<i class="fas fa-check" style="color: #4CAF50;"></i>';
      
      // Reset button after 2 seconds
      setTimeout(() => {
        button.innerHTML = originalContent;
        button.disabled = false;
      }, 2000);
      
    } catch (error) {
      console.error("Download failed:", error);
      button.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #f44336;"></i>';
      
      // Reset button after 2 seconds
      setTimeout(() => {
        button.innerHTML = originalContent;
        button.disabled = false;
      }, 2000);
    }
  }

  async onSearch(event) {
    const query = event.target.value.trim();

    if (!query) {
      this.loadEmails();
      return;
    }

    // Parse Gmail-style search syntax
    const filters = EmailAPIClient.parseSearchQuery(query);
    this.loadEmails(null, filters);
  }

  showEmailList() {
    this.currentEmailId = null;
    this.emailDetailContainer.style.display = "none";
    this.emailListContainer.style.display = "block";
    this.emailListContainer.querySelectorAll(".email-item").forEach((item) => {
      item.classList.remove("active");
    });
  }

  onReply() {
    alert("Reply feature coming soon!");
  }

  onDelete() {
    if (confirm("Are you sure you want to delete this email?")) {
      alert("Delete feature coming soon!");
    }
  }

  // ================= FILTER PANEL METHODS =================

  openFilterPanel() {
    this.filterPanel.classList.add("active");
    this.filterPanelOverlay.classList.add("active");
    document.body.style.overflow = "hidden";
  }

  closeFilterPanel() {
    this.filterPanel.classList.remove("active");
    this.filterPanelOverlay.classList.remove("active");
    document.body.style.overflow = "auto";
  }

  collectFilterValues() {
    const startDateValue = document.getElementById("filterStartDate").value;
    const endDateValue = document.getElementById("filterEndDate").value;

    // Convert date format from YYYY-MM-DD to ISO 8601 datetime format with milliseconds and Z timezone
    // start_date defaults to 00:00:00.000Z, end_date defaults to 23:59:59.999Z
    const start_date = startDateValue ? `${startDateValue}T00:00:00.000Z` : null;
    const end_date = endDateValue ? `${endDateValue}T23:59:59.999Z` : null;

    // Parse to_addresses (comma-separated to array)
    const toAddresses = document.getElementById("filterTo").value
      .split(",")
      .map((x) => x.trim())
      .filter((x) => x);
    
    // Parse has_words (comma-separated to array)
    const hasWords = document.getElementById("filterWords").value
      .split(",")
      .map((x) => x.trim())
      .filter((x) => x);

    return {
      from_address: document.getElementById("filterFrom").value.trim() || null,
      to_addresses: toAddresses.length > 0 ? toAddresses : null,
      subject_contains: document.getElementById("filterSubject").value.trim() || null,
      body_contains: document.getElementById("filterBody").value.trim() || null,
      has_words: hasWords.length > 0 ? hasWords : null,
      start_date: start_date,
      end_date: end_date,
      has_attachments: document.getElementById("filterHasAttachments").checked ? true : null,
      is_read: this.getReadStatusFilter(),
    };
  }

  getReadStatusFilter() {
    const readStatus = document.querySelector('input[name="readStatus"]:checked').value;
    if (readStatus === "read") return true;
    if (readStatus === "unread") return false;
    return null;
  }

  async applyFilters() {
    if (!this.currentProvider) {
      alert("Please select an email provider first");
      return;
    }

    const filters = this.collectFilterValues();

    // Check if any filter is set
    const hasAnyFilter = Object.values(filters).some((v) => v !== null && v !== false);

    if (!hasAnyFilter) {
      alert("Please set at least one filter");
      return;
    }

    // Close the filter panel
    this.closeFilterPanel();

    // Load emails with filters
    await this.loadEmails(null, filters);
  }

  clearFilters() {
    document.getElementById("filterFrom").value = "";
    document.getElementById("filterTo").value = "";
    document.getElementById("filterSubject").value = "";
    document.getElementById("filterBody").value = "";
    document.getElementById("filterWords").value = "";
    document.getElementById("filterStartDate").value = "";
    document.getElementById("filterEndDate").value = "";
    document.getElementById("filterHasAttachments").checked = false;
    document.querySelector('input[name="readStatus"][value="all"]').checked = true;
  }

  // ================= UTILITY FUNCTIONS =================

  parseSender(senderString) {
    // Parse sender string like "John Doe <john@example.com>" or just "john@example.com"
    const emailMatch = senderString.match(/<([^>]+)>/);
    const email = emailMatch ? emailMatch[1] : senderString.trim();
    const name = senderString.replace(/<[^>]+>/, "").trim() || email;
    return { email, name };
  }

  getInitials(emailAddress) {
    if (!emailAddress) return "?";
    const parts = emailAddress.split("@")[0].split(".");
    return parts.map((p) => p[0]).join("").toUpperCase().slice(0, 2);
  }

  getAvatarColor(emailAddress) {
    // Generate consistent color based on email address
    const colors = [
      "#667eea", // Purple
      "#764ba2", // Deep Purple
      "#f093fb", // Pink
      "#4facfe", // Blue
      "#00f2fe", // Cyan
      "#43e97b", // Green
      "#fa709a", // Red
      "#fee140", // Yellow
      "#30cfd0", // Turquoise
      "#330867"  // Dark Purple
    ];

    if (!emailAddress) return colors[0];
    
    // Hash the email to get consistent color
    let hash = 0;
    for (let i = 0; i < emailAddress.length; i++) {
      hash = emailAddress.charCodeAt(i) + ((hash << 5) - hash);
    }
    
    return colors[Math.abs(hash) % colors.length];
  }

  shadeColor(color, percent) {
    // Darken or lighten a color
    let R = parseInt(color.substring(1,3),16);
    let G = parseInt(color.substring(3,5),16);
    let B = parseInt(color.substring(5,7),16);

    R = parseInt(R * (100 + percent) / 100);
    G = parseInt(G * (100 + percent) / 100);
    B = parseInt(B * (100 + percent) / 100);

    R = (R<255)?R:255;
    G = (G<255)?G:255;
    B = (B<255)?B:255;

    const RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
    const GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
    const BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

    return "#"+RR+GG+BB;
  }

  truncate(text, length) {
    return text.length > length ? text.slice(0, length) + "..." : text;
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric"
    });
  }

  formatDateLong(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit"
    });
  }

  formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + " " + sizes[i];
  }

  sanitizeHtml(html) {
    // For email HTML, we want to preserve most formatting but remove dangerous elements
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = html;

    // Remove only truly dangerous elements
    const dangerousElements = tempDiv.querySelectorAll(
      "script, iframe, object, embed"
    );
    dangerousElements.forEach((el) => el.remove());

    // Remove event handlers from all elements
    const allElements = tempDiv.querySelectorAll("*");
    allElements.forEach((el) => {
      Array.from(el.attributes).forEach((attr) => {
        if (attr.name.startsWith("on")) {
          el.removeAttribute(attr.name);
        }
      });
    });

    // Return sanitized HTML
    return tempDiv.innerHTML;
  }

  showError(title, error) {
    console.error(`${title}:`, error);
    // Could show toast notification here
  }
}

// Initialize app when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  window.emailClient = new EmailClientApp();
});
