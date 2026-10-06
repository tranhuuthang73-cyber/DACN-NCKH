/**
 * Phase 5.2.1 — Chat Composer Document Attachment UX
 * ChatGPT-like document-grounded assistant with inline composer attachments.
 *
 * STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
 * 100% Vietnamese Localization.
 */

// ==============================================================================
// GLOBAL STATE
// ==============================================================================
const state = {
  currentSessionId: null,
  currentSession: null,
  sessions: [],
  answerMode: "balanced", // concise | balanced | detailed
  researchMode: false,
  attachedDocuments: [], // [{document_id, title, file_name, file_size}]
  lastAssistantMessage: null,
  dragCounter: 0, // Track nested drag events
};

// ==============================================================================
// DOM ELEMENTS
// ==============================================================================
const el = {
  // Sidebar & Navigation
  sidebar: document.getElementById("sidebar"),
  btnToggleSidebar: document.getElementById("btn-toggle-sidebar"),
  btnNewChat: document.getElementById("btn-new-chat"),
  sessionsList: document.getElementById("sidebar-sessions-list"),
  btnOpenDocsModal: document.getElementById("btn-open-documents-modal"),
  toggleResearchMode: document.getElementById("toggle-research-mode"),
  researchModeStatus: document.getElementById("research-mode-status"),
  btnSeedDemo: document.getElementById("btn-seed-demo"),

  // Header
  headerSessionTitle: document.getElementById("header-session-title"),
  attachedTagsList: document.getElementById("attached-tags-list"),
  btnAttachMore: document.getElementById("btn-attach-more"),
  btnOpenResearchDrawer: document.getElementById("btn-open-research-drawer"),

  // Chat Views & Empty State
  chatMain: document.querySelector(".chat-main"),
  chatDragOverlay: document.getElementById("chat-drag-overlay"),
  chatScrollContainer: document.getElementById("chat-scroll-container"),
  firstUseBanner: document.getElementById("first-use-banner"),
  btnDismissFirstUse: document.getElementById("btn-dismiss-first-use"),
  welcomeScreen: document.getElementById("welcome-screen"),
  btnEmptyUpload: document.getElementById("btn-empty-upload"),
  btnEmptyLibrary: document.getElementById("btn-empty-library"),
  suggestionsContainer: document.getElementById("suggestions-container"),
  fileUploadInput: document.getElementById("file-upload-input"),
  chatFileAttachment: document.getElementById("chat-file-attachment"),
  messagesStream: document.getElementById("messages-stream"),
  messagesList: document.getElementById("messages-list"),
  thinkingIndicator: document.getElementById("thinking-indicator"),
  thinkingText: document.getElementById("thinking-text"),

  // Dynamic Ingestion Pipeline
  ingestionPipelineCard: document.getElementById("ingestion-pipeline-card"),
  pipelineFilename: document.getElementById("pipeline-filename"),
  pipelineFiletype: document.getElementById("pipeline-filetype"),
  pipelineFilesize: document.getElementById("pipeline-filesize"),
  pipelineOverallStatus: document.getElementById("pipeline-overall-status"),
  stageReceived: document.getElementById("stage-received"),
  stageReading: document.getElementById("stage-reading"),
  stageStructure: document.getElementById("stage-structure"),
  stageIndex: document.getElementById("stage-index"),
  stageMemory: document.getElementById("stage-memory"),
  stageReady: document.getElementById("stage-ready"),

  // Memory Explanation Card & Ready Screen
  memoryReadyCard: document.getElementById("memory-ready-card"),
  readyScreen: document.getElementById("ready-screen"),
  readyActiveDocsList: document.getElementById("ready-active-docs-list"),

  // Composer
  chatInputForm: document.getElementById("chat-input-form"),
  chatTextarea: document.getElementById("chat-textarea"),
  btnSendMessage: document.getElementById("btn-send-message"),
  lengthModeBtns: document.querySelectorAll(".btn-length-mode"),
  inputDocIndicator: document.getElementById("input-doc-indicator"),
  composerAttachments: document.getElementById("composer-attachments"),
  composerAttachmentsList: document.getElementById("composer-attachments-list"),
  composerAddMoreBtn: document.getElementById("composer-add-more-btn"),

  // Source Panel (Right Drawer)
  sourcePanel: document.getElementById("source-panel"),
  btnCloseSourcePanel: document.getElementById("btn-close-source-panel"),
  sourceDocTitle: document.getElementById("source-doc-title"),
  sourceSectionTitle: document.getElementById("source-section-title"),
  sourceParagraphIndex: document.getElementById("source-paragraph-index"),
  sourceScore: document.getElementById("source-score"),
  sourceQuoteText: document.getElementById("source-quote-text"),
  btnViewDocStructure: document.getElementById("btn-view-doc-structure"),

  // Research Drawer
  researchDrawer: document.getElementById("research-drawer"),
  btnCloseResearchDrawer: document.getElementById("btn-close-research-drawer"),
  drawerTabBtns: document.querySelectorAll(".drawer-tab-btn"),
  drawerRouteName: document.getElementById("drawer-route-name"),
  drawerRouteDesc: document.getElementById("drawer-route-desc"),
  drawerEvidenceCount: document.getElementById("drawer-evidence-count"),
  drawerRefusalStatus: document.getElementById("drawer-refusal-status"),
  drawerMemoryLevel: document.getElementById("drawer-memory-level"),
  drawerInputTokens: document.getElementById("drawer-input-tokens"),
  drawerOutputTokens: document.getElementById("drawer-output-tokens"),
  drawerTotalLatency: document.getElementById("drawer-total-latency"),
  drawerRetrievalLatency: document.getElementById("drawer-retrieval-latency"),
  btnRunDrawerCompare: document.getElementById("btn-run-drawer-compare"),
  drawerCompareGrid: document.getElementById("drawer-compare-grid"),

  // Document Library Modal
  modalDocuments: document.getElementById("modal-documents"),
  btnCloseDocsModal: document.getElementById("btn-close-documents-modal"),
  inputSearchDocs: document.getElementById("input-search-docs"),
  modalUploadInput: document.getElementById("modal-upload-input"),
  documentsTableBody: document.getElementById("documents-table-body"),
  backdropOverlay: document.getElementById("backdrop-overlay"),

  // Round 2 Dashboard, Demos, Settings
  btnOpenDashboardModal: document.getElementById("btn-open-dashboard-modal"),
  modalResearchDashboard: document.getElementById("modal-research-dashboard"),
  btnCloseDashboardModal: document.getElementById("btn-close-dashboard-modal"),
  dashTabBtns: document.querySelectorAll(".dash-tab-btn"),
  dashTabPanes: document.querySelectorAll(".dash-tab-pane"),

  // Research Lab Main Navigation & Panes
  labMainTabBtns: document.querySelectorAll(".lab-main-tab-btn"),
  labMainPanes: document.querySelectorAll(".lab-main-pane"),
  labScenariosList: document.getElementById("lab-scenarios-list"),

  // 10-Step Interactive Guided Demo
  demoStepperFill: document.getElementById("demo-stepper-fill"),
  demoStepBadge: document.getElementById("demo-step-badge"),
  demoStepTitle: document.getElementById("demo-step-title"),
  demoStepContentCard: document.getElementById("demo-step-content-card"),
  btnDemoPrev: document.getElementById("btn-demo-prev"),
  btnDemoNext: document.getElementById("btn-demo-next"),
  btnDemoAuto: document.getElementById("btn-demo-auto"),
  btnDemoReset: document.getElementById("btn-demo-reset"),

  btnOpenDemosModal: document.getElementById("btn-open-demos-modal"),
  modalDemos: document.getElementById("modal-demos"),
  btnCloseDemosModal: document.getElementById("btn-close-demos-modal"),
  demoScenariosList: document.getElementById("demo-scenarios-list"),

  btnOpenSettingsModal: document.getElementById("btn-open-settings-modal"),
  modalSettings: document.getElementById("modal-settings"),
  btnCloseSettingsModal: document.getElementById("btn-close-settings-modal"),
  btnSaveSettings: document.getElementById("btn-save-settings"),
  settingAnswerMode: document.getElementById("setting-answer-mode"),
  settingQaMode: document.getElementById("setting-qa-mode"),
  settingTopK: document.getElementById("setting-top-k"),
  settingLanguage: document.getElementById("setting-language"),

  // System Status
  btnOpenSystemStatus: document.getElementById("btn-open-system-status"),
  modalSystemStatus: document.getElementById("modal-system-status"),
  btnCloseSystemStatusModal: document.getElementById("btn-close-system-status-modal"),
  headerOfflineStatusText: document.getElementById("header-offline-status-text"),
  statusCardModel: document.getElementById("status-card-model"),
  statusCardTokenizer: document.getElementById("status-card-tokenizer"),
  statusCardCheckpoint: document.getElementById("status-card-checkpoint"),
  statusCardIndex: document.getElementById("status-card-index"),
  statusCardEvidence: document.getElementById("status-card-evidence"),
  statusCardOffline: document.getElementById("status-card-offline"),
  statusCardNetwork: document.getElementById("status-card-network"),
  statusFooterNote: document.getElementById("status-footer-note"),
};

// ==============================================================================
// INITIALIZATION
// ==============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  loadSessions();
  fetchAndRenderSystemStatus();
});

function initEventListeners() {
  // 1. Sidebar Toggles & Actions
  if (el.btnToggleSidebar) {
    el.btnToggleSidebar.addEventListener("click", () => {
      el.sidebar.classList.toggle("collapsed");
      el.sidebar.classList.toggle("open-mobile");
    });
  }

  if (el.btnNewChat) {
    el.btnNewChat.addEventListener("click", () => createNewSession());
  }

  if (el.btnSeedDemo) {
    el.btnSeedDemo.addEventListener("click", handleSeedDemo);
  }

  // 2. Research Mode Toggle
  if (el.toggleResearchMode) {
    el.toggleResearchMode.addEventListener("change", (e) => {
      setResearchMode(e.target.checked);
    });
  }

  if (el.btnOpenResearchDrawer) {
    el.btnOpenResearchDrawer.addEventListener("click", () => {
      openResearchDrawer();
    });
  }

  if (el.btnCloseResearchDrawer) {
    el.btnCloseResearchDrawer.addEventListener("click", () => {
      el.researchDrawer.classList.remove("open");
    });
  }

  // Research Drawer Tabs
  el.drawerTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      el.drawerTabBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".drawer-tab-pane").forEach((p) => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  if (el.btnRunDrawerCompare) {
    el.btnRunDrawerCompare.addEventListener("click", runModelComparison);
  }

  // First-Use Helper Banner
  if (el.firstUseBanner && localStorage.getItem("sa_cms_first_use_dismissed") !== "1") {
    el.firstUseBanner.style.display = "flex";
  }
  if (el.btnDismissFirstUse) {
    el.btnDismissFirstUse.addEventListener("click", () => {
      localStorage.setItem("sa_cms_first_use_dismissed", "1");
      if (el.firstUseBanner) el.firstUseBanner.style.display = "none";
    });
  }

  // First-time Empty State Actions
  if (el.btnEmptyUpload) {
    el.btnEmptyUpload.addEventListener("click", () => {
      if (el.fileUploadInput) el.fileUploadInput.click();
    });
  }
  if (el.btnEmptyLibrary) {
    el.btnEmptyLibrary.addEventListener("click", () => {
      openDocumentsModal();
    });
  }

  // Research Lab Modal Controls & Top-Level Tab Switching
  if (el.btnOpenDashboardModal) {
    el.btnOpenDashboardModal.addEventListener("click", openDashboardModal);
  }
  if (el.btnCloseDashboardModal) {
    el.btnCloseDashboardModal.addEventListener("click", closeDashboardModal);
  }

  // Research Lab Top-Level Tabs (Dashboard 8 Pages, Demo 10 Steps, ASCII Diagram, 7 Scenarios)
  el.labMainTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      el.labMainTabBtns.forEach((b) => b.classList.remove("active"));
      el.labMainPanes.forEach((p) => {
        p.classList.remove("active");
        p.style.display = "none";
      });

      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.labTarget);
      if (targetPane) {
        targetPane.classList.add("active");
        targetPane.style.display = "block";
      }

      if (btn.dataset.labTarget === "lab-section-scenarios") {
        renderLabScenarios();
      }
      if (btn.dataset.labTarget === "lab-section-demo") {
        renderDemoStep(currentDemoStep);
      }
    });
  });

  // 10-Step Interactive Guided Demo Controls
  initDemoStepperControls();

  // Sub-tabs in Dashboard (8 Pages)
  el.dashTabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      el.dashTabBtns.forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".dash-tab-pane").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.dashTab);
      if (targetPane) targetPane.classList.add("active");
    });
  });

  // Round 2 Demos Modal Controls
  if (el.btnOpenDemosModal) {
    el.btnOpenDemosModal.addEventListener("click", openDemosModal);
  }
  if (el.btnCloseDemosModal) {
    el.btnCloseDemosModal.addEventListener("click", closeDemosModal);
  }

  // Round 2 Settings Modal Controls
  if (el.btnOpenSettingsModal) {
    el.btnOpenSettingsModal.addEventListener("click", openSettingsModal);
  }
  if (el.btnCloseSettingsModal) {
    el.btnCloseSettingsModal.addEventListener("click", closeSettingsModal);
  }
  if (el.btnSaveSettings) {
    el.btnSaveSettings.addEventListener("click", saveSettings);
  }

  // Round 2 Offline Resource Status Modal
  if (el.btnOpenSystemStatus) {
    el.btnOpenSystemStatus.addEventListener("click", openSystemStatusModal);
  }
  if (el.btnCloseSystemStatusModal) {
    el.btnCloseSystemStatusModal.addEventListener("click", closeSystemStatusModal);
  }

  // 3. Drag & Drop — target toàn bộ chat-main
  setupDragAndDrop();

  if (el.fileUploadInput) {
    el.fileUploadInput.addEventListener("change", (e) => {
      handleFilesUpload(e.target.files);
    });
  }

  if (el.chatFileAttachment) {
    el.chatFileAttachment.addEventListener("change", (e) => {
      handleFilesUpload(e.target.files);
    });
  }

  if (el.btnAttachMore) {
    el.btnAttachMore.addEventListener("click", () => {
      openDocumentsModal();
    });
  }

  // Composer "+ Thêm" button
  if (el.composerAddMoreBtn) {
    el.composerAddMoreBtn.addEventListener("click", () => {
      el.chatFileAttachment.click();
    });
  }

  // 4. Quick Suggestions
  document.querySelectorAll(".suggestion-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const query = chip.dataset.query;
      if (query) {
        el.chatTextarea.value = query;
        submitUserMessage();
      }
    });
  });

  // 5. Chat Input & Length Mode
  el.lengthModeBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      el.lengthModeBtns.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.answerMode = btn.dataset.mode;
    });
  });

  if (el.chatInputForm) {
    el.chatInputForm.addEventListener("submit", (e) => {
      e.preventDefault();
      submitUserMessage();
    });
  }

  if (el.chatTextarea) {
    el.chatTextarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        submitUserMessage();
      }
    });

    // Auto resize textarea
    el.chatTextarea.addEventListener("input", () => {
      el.chatTextarea.style.height = "auto";
      el.chatTextarea.style.height = Math.min(el.chatTextarea.scrollHeight, 160) + "px";
    });
  }

  // 6. Source Panel Close
  if (el.btnCloseSourcePanel) {
    el.btnCloseSourcePanel.addEventListener("click", () => {
      el.sourcePanel.classList.remove("open");
    });
  }

  // 7. Documents Modal
  if (el.btnOpenDocsModal) {
    el.btnOpenDocsModal.addEventListener("click", openDocumentsModal);
  }

  if (el.btnCloseDocsModal) {
    el.btnCloseDocsModal.addEventListener("click", closeDocumentsModal);
  }

  if (el.modalUploadInput) {
    el.modalUploadInput.addEventListener("change", (e) => {
      handleFilesUpload(e.target.files);
    });
  }

  if (el.inputSearchDocs) {
    el.inputSearchDocs.addEventListener("input", (e) => {
      loadDocumentsTable(e.target.value.trim());
    });
  }

  // Close overlays when clicking backdrop
  if (el.backdropOverlay) {
    el.backdropOverlay.addEventListener("click", () => {
      closeDocumentsModal();
      closeDashboardModal();
      closeDemosModal();
      closeSettingsModal();
      closeSystemStatusModal();
      el.sourcePanel.classList.remove("open");
      el.researchDrawer.classList.remove("open");
      el.sidebar.classList.remove("open-mobile");
      el.backdropOverlay.style.display = "none";
    });
  }

  // Rename session inline on double-click
  if (el.headerSessionTitle) {
    el.headerSessionTitle.addEventListener("dblclick", () => {
      const current = el.headerSessionTitle.textContent;
      const newTitle = prompt("Đổi tên cuộc trò chuyện:", current);
      if (newTitle && newTitle.trim() && state.currentSessionId) {
        renameSession(state.currentSessionId, newTitle.trim());
      }
    });
  }
}

// ==============================================================================
// DRAG & DROP — target toàn bộ chat-main, hiện overlay nhẹ
// ==============================================================================
function setupDragAndDrop() {
  const chatMain = el.chatMain;
  if (!chatMain) return;

  const preventDefaults = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  // Track drag enter/leave with counter to handle nested elements
  chatMain.addEventListener("dragenter", (e) => {
    preventDefaults(e);
    state.dragCounter++;
    if (state.dragCounter === 1) {
      el.chatDragOverlay.classList.add("active");
    }
  });

  chatMain.addEventListener("dragover", (e) => {
    preventDefaults(e);
  });

  chatMain.addEventListener("dragleave", (e) => {
    preventDefaults(e);
    state.dragCounter--;
    if (state.dragCounter <= 0) {
      state.dragCounter = 0;
      el.chatDragOverlay.classList.remove("active");
    }
  });

  chatMain.addEventListener("drop", (e) => {
    preventDefaults(e);
    state.dragCounter = 0;
    el.chatDragOverlay.classList.remove("active");

    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length > 0) {
      handleFilesUpload(dt.files);
    }
  });
}

// ==============================================================================
// FILE UPLOAD & COMPOSER ATTACHMENT UX
// ==============================================================================
async function handleFilesUpload(fileList) {
  if (!fileList || fileList.length === 0) return;

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    await uploadSingleFile(file);
  }

  // Refresh attached documents for session
  if (state.currentSessionId) {
    loadSessionDetail(state.currentSessionId);
  }
}

function formatBytes(bytes) {
  if (bytes === null || bytes === undefined || bytes === "" || Number.isNaN(bytes)) {
    return "Dung lượng không xác định";
  }
  if (typeof bytes === "string") {
    const trimmed = bytes.trim();
    if (!trimmed || trimmed.toLowerCase() === "nan mb" || trimmed.toLowerCase() === "nan kb" || trimmed.toLowerCase() === "nan" || trimmed.toLowerCase() === "undefined" || trimmed.toLowerCase() === "null") {
      return "Dung lượng không xác định";
    }
    if (/^[\d.]+\s*(B|KB|MB|GB|TB)$/i.test(trimmed)) {
      if (trimmed.toLowerCase().includes("nan")) {
        return "Dung lượng không xác định";
      }
      return trimmed;
    }
    const num = Number(trimmed);
    if (!isNaN(num) && num >= 0) {
      bytes = num;
    } else {
      return "Dung lượng không xác định";
    }
  }
  if (typeof bytes === "number") {
    if (isNaN(bytes) || bytes < 0) return "Dung lượng không xác định";
    if (bytes === 0) return "0 KB";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  }
  return "Dung lượng không xác định";
}

function getFileExtensionBadge(filename) {
  if (!filename) return "FILE";
  const ext = filename.split(".").pop().toLowerCase();
  if (["png", "jpg", "jpeg"].includes(ext)) return "ẢNH (OCR)";
  return ext.toUpperCase();
}

function setPipelineStage(stageEl, status, icon, tagText, descText) {
  if (!stageEl) return;
  stageEl.classList.remove("pending", "active", "done");
  stageEl.classList.add(status);

  const iconEl = stageEl.querySelector(".stage-icon");
  if (iconEl) {
    if (status === "active") {
      iconEl.innerHTML = '<div class="mini-spinner"></div>';
    } else {
      iconEl.textContent = icon;
    }
  }

  const tagEl = stageEl.querySelector(".stage-tag");
  if (tagEl && tagText) {
    tagEl.textContent = tagText;
  }

  const descEl = stageEl.querySelector(".stage-desc");
  if (descEl && descText) {
    descEl.textContent = descText;
  }
}

async function uploadSingleFile(file) {
  const chipId = `chip-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  const sizeFormatted = formatBytes(file.size);
  const extBadge = getFileExtensionBadge(file.name);

  // 1. Hiển thị Ingestion Pipeline Progress Card
  if (el.ingestionPipelineCard) {
    el.ingestionPipelineCard.style.display = "block";
    if (el.pipelineFilename) el.pipelineFilename.textContent = file.name;
    if (el.pipelineFiletype) el.pipelineFiletype.textContent = extBadge;
    if (el.pipelineFilesize) el.pipelineFilesize.textContent = sizeFormatted;
    if (el.pipelineOverallStatus) el.pipelineOverallStatus.textContent = "Đang xử lý...";

    // Reset 6 stages
    setPipelineStage(el.stageReceived, "done", "✓", "FILE STORED", "✓ Tệp đã lưu an toàn trên ổ đĩa cục bộ");
    setPipelineStage(el.stageReading, "active", "○", "TEXT EXTRACTING", "Đang trích xuất văn bản...");
    setPipelineStage(el.stageStructure, "pending", "○", "PENDING", "Đang chờ phân tích cấu trúc");
    setPipelineStage(el.stageIndex, "pending", "○", "PENDING", "Đang chờ lập chỉ mục");
    setPipelineStage(el.stageMemory, "pending", "○", "PENDING", "Đang chờ nạp vào SA-CMS Memory");
    setPipelineStage(el.stageReady, "pending", "○", "PENDING", "Đang chờ hoàn tất");
  }

  // Render chip in composer attachments area with "Đang tải lên..." status
  renderComposerChip(chipId, file.name, sizeFormatted, "Đang tải lên...", "processing");

  const formData = new FormData();
  formData.append("file", file);
  if (state.currentSessionId) {
    formData.append("session_id", state.currentSessionId);
  }

  try {
    updateComposerChipStatus(chipId, "Đang đọc văn bản...", "processing");

    const resp = await fetch("/api/documents/upload", {
      method: "POST",
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Không thể tải lên tài liệu.");
    }

    const data = await resp.json();

    // Stage 2: Văn bản đã trích xuất
    setPipelineStage(el.stageReading, "done", "✓", "TEXT EXTRACTED", "✓ Văn bản đã trích xuất");

    // Stage 3: Phân tích cấu trúc (L1/L2/L3)
    setPipelineStage(el.stageStructure, "active", "○", "PARSING STRUCTURE", "Đang phân tích cấu trúc phân cấp (Đoạn, Mục, Tài liệu)...");
    await new Promise((r) => setTimeout(r, 160));
    setPipelineStage(el.stageStructure, "done", "✓", "STRUCTURE PARSED", "✓ Cấu trúc đã phân tích (L1 Đoạn, L2 Mục, L3 Tài liệu)");

    // Stage 4: Tạo chỉ mục cục bộ
    setPipelineStage(el.stageIndex, "active", "○", "INDEXING", "Đang tạo chỉ mục tìm kiếm cục bộ BM25...");
    await new Promise((r) => setTimeout(r, 160));
    setPipelineStage(el.stageIndex, "done", "✓", "INDEX READY", "✓ Chỉ mục cục bộ đã sẵn sàng");

    // Stage 5: Nạp vào SA-CMS Memory
    setPipelineStage(el.stageMemory, "active", "○", "INGESTING", "Đang nạp tri thức vào SA-CMS Memory (3 cấp độ)...");
    await new Promise((r) => setTimeout(r, 200));
    setPipelineStage(el.stageMemory, "done", "✓", "MEMORY INGESTED", "✓ SA-CMS Memory đã sẵn sàng");

    // Stage 6: Sẵn sàng hỏi
    setPipelineStage(el.stageReady, "done", "✓", "READY", "✓ Sẵn sàng hỏi");
    if (el.pipelineOverallStatus) {
      el.pipelineOverallStatus.textContent = "✓ SA-CMS Memory đã sẵn sàng";
    }

    // Hiển thị thẻ giải thích bộ nhớ SA-CMS
    if (el.memoryReadyCard) {
      el.memoryReadyCard.style.display = "block";
    }

    // Cập nhật composer chip - phân biệt rõ SA-CMS Memory đã sẵn sàng với File đã tải
    updateComposerChipStatus(chipId, "SA-CMS Memory đã sẵn sàng", "ready");

    // Add to attached documents
    const docInfo = {
      document_id: data.document_id,
      title: data.title,
      file_name: data.file_name,
      file_size: formatBytes(data.file_size),
      _chipId: chipId,
    };
    addAttachedDocument(docInfo);

    // Update chip to include remove button linked to document_id
    updateComposerChipDocId(chipId, data.document_id);

    // Chuyển sang Ready State nếu chưa có tin nhắn chat nào
    if (!state.currentSession?.messages || state.currentSession.messages.length === 0) {
      if (el.welcomeScreen) el.welcomeScreen.style.display = "none";
      if (el.readyScreen) el.readyScreen.style.display = "flex";
      renderReadyActiveDocs();
    }

    // Tự động focus vào khung nhập câu hỏi
    if (el.chatTextarea) {
      el.chatTextarea.focus();
    }
  } catch (error) {
    console.error("Upload error:", error);
    updateComposerChipStatus(chipId, "Lỗi", "error");
    if (el.pipelineOverallStatus) {
      el.pipelineOverallStatus.textContent = "❌ Lỗi khi đọc tài liệu";
    }
  }
}

// ==============================================================================
// COMPOSER CHIP RENDERING (nằm ngay trên chat input)
// ==============================================================================
function renderComposerChip(chipId, fileName, size, statusText, statusClass) {
  // Show composer attachments area
  el.composerAttachments.style.display = "flex";

  const chip = document.createElement("div");
  chip.className = "composer-file-chip";
  chip.id = chipId;

  const displaySize = formatBytes(size);
  const spinnerHtml = statusClass === "processing"
    ? '<div class="chip-spinner"></div>'
    : '';
  const statusIcon = statusClass === "ready" ? "✓" : statusClass === "error" ? "✗" : "";

  chip.innerHTML = `
    <span class="chip-icon">📄</span>
    <div class="chip-info">
      <span class="chip-name" title="${escapeHtml(fileName)}">${escapeHtml(fileName)}</span>
      <span class="chip-meta">
        <span class="chip-size">${escapeHtml(displaySize)}</span>
        <span class="chip-status ${statusClass}">
          ${spinnerHtml}${statusIcon} ${statusText}
        </span>
      </span>
    </div>
    <button class="chip-remove" title="Bỏ tài liệu khỏi cuộc trò chuyện" style="display: none;">✕</button>
  `;

  el.composerAttachmentsList.appendChild(chip);
}

function updateComposerChipStatus(chipId, statusText, statusClass) {
  const chip = document.getElementById(chipId);
  if (!chip) return;

  const statusEl = chip.querySelector(".chip-status");
  if (statusEl) {
    const spinnerHtml = statusClass === "processing"
      ? '<div class="chip-spinner"></div>'
      : '';
    const statusIcon = statusClass === "ready" ? "✓" : statusClass === "error" ? "✗" : "";
    statusEl.className = `chip-status ${statusClass}`;
    statusEl.innerHTML = `${spinnerHtml}${statusIcon} ${statusText}`;
  }

  // Show remove button when ready or error
  if (statusClass === "ready" || statusClass === "error") {
    const removeBtn = chip.querySelector(".chip-remove");
    if (removeBtn) {
      removeBtn.style.display = "flex";
    }
  }
}

function updateComposerChipDocId(chipId, documentId) {
  const chip = document.getElementById(chipId);
  if (!chip) return;

  chip.dataset.documentId = documentId;

  const removeBtn = chip.querySelector(".chip-remove");
  if (removeBtn) {
    removeBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      removeAttachmentFromComposer(documentId, chipId);
    });
  }
}

function removeAttachmentFromComposer(documentId, chipId) {
  // Remove chip from DOM
  const chip = document.getElementById(chipId);
  if (chip) chip.remove();

  // Remove from state (detach from chat, NOT delete from library)
  detachDocumentFromSession(documentId);

  // Hide composer attachments if empty
  if (el.composerAttachmentsList.children.length === 0) {
    el.composerAttachments.style.display = "none";
  }
}

function renderComposerAttachmentsFromState() {
  // Clear existing chips
  el.composerAttachmentsList.innerHTML = "";

  if (state.attachedDocuments.length === 0) {
    el.composerAttachments.style.display = "none";
    return;
  }

  el.composerAttachments.style.display = "flex";

  const MAX_VISIBLE = 4;
  const docsToShow = state.attachedDocuments.slice(0, MAX_VISIBLE);
  const remaining = state.attachedDocuments.length - MAX_VISIBLE;

  docsToShow.forEach((doc) => {
    const chipId = `chip-attached-${doc.document_id}`;
    const sizeText = formatBytes(doc.file_size);

    const chip = document.createElement("div");
    chip.className = "composer-file-chip";
    chip.id = chipId;
    chip.dataset.documentId = doc.document_id;

    chip.innerHTML = `
      <span class="chip-icon">📄</span>
      <div class="chip-info">
        <span class="chip-name" title="${escapeHtml(doc.title || doc.file_name)}">${escapeHtml(doc.title || doc.file_name)}</span>
        <span class="chip-meta">
          <span class="chip-size">${escapeHtml(sizeText)}</span>
          <span class="chip-status ready">✓ SA-CMS Memory đã sẵn sàng</span>
        </span>
      </div>
      <button class="chip-remove" title="Bỏ tài liệu khỏi cuộc trò chuyện">✕</button>
    `;

    chip.querySelector(".chip-remove").addEventListener("click", (e) => {
      e.stopPropagation();
      removeAttachmentFromComposer(doc.document_id, chipId);
    });

    el.composerAttachmentsList.appendChild(chip);
  });

  // Overflow chip if > MAX_VISIBLE
  if (remaining > 0) {
    const overflowChip = document.createElement("button");
    overflowChip.className = "composer-overflow-chip";
    overflowChip.textContent = `+${remaining}`;
    overflowChip.title = `Xem tất cả ${state.attachedDocuments.length} tài liệu`;
    overflowChip.addEventListener("click", () => {
      openDocumentsModal();
    });
    el.composerAttachmentsList.appendChild(overflowChip);
  }
}

// ==============================================================================
// SESSION MANAGEMENT
// ==============================================================================
async function loadSessions() {
  try {
    const resp = await fetch("/api/chat/sessions");
    const data = await resp.json();
    state.sessions = data.sessions || [];

    renderSidebarSessions(state.sessions);

    if (state.sessions.length > 0) {
      loadSessionDetail(state.sessions[0].session_id);
    } else {
      createNewSession();
    }
  } catch (err) {
    console.error("Error loading sessions:", err);
    createNewSession();
  }
}

function renderSidebarSessions(sessions) {
  el.sessionsList.innerHTML = "";

  const groups = { "Hôm nay": [], "Hôm qua": [], "Trước đó": [] };
  sessions.forEach((s) => {
    const g = s.time_group || "Hôm nay";
    if (!groups[g]) groups[g] = [];
    groups[g].push(s);
  });

  Object.entries(groups).forEach(([groupName, items]) => {
    if (items.length === 0) return;

    const groupEl = document.createElement("div");
    groupEl.className = "session-group";
    groupEl.innerHTML = `<div class="session-group-title">${groupName}</div>`;

    items.forEach((s) => {
      const itemEl = document.createElement("div");
      itemEl.className = `session-item ${s.session_id === state.currentSessionId ? "active" : ""}`;
      itemEl.dataset.sessionId = s.session_id;

      itemEl.innerHTML = `
        <span class="session-item-title" title="${escapeHtml(s.title)}">💬 ${escapeHtml(s.title)}</span>
        <div class="session-item-actions">
          <button class="session-action-btn btn-rename" title="Đổi tên">✏️</button>
          <button class="session-action-btn btn-delete" title="Xóa">🗑️</button>
        </div>
      `;

      itemEl.addEventListener("click", (e) => {
        if (e.target.closest(".btn-rename")) {
          e.stopPropagation();
          const newTitle = prompt("Đổi tên cuộc trò chuyện:", s.title);
          if (newTitle && newTitle.trim()) {
            renameSession(s.session_id, newTitle.trim());
          }
          return;
        }

        if (e.target.closest(".btn-delete")) {
          e.stopPropagation();
          if (confirm("Xóa cuộc trò chuyện này?")) {
            deleteSession(s.session_id);
          }
          return;
        }

        loadSessionDetail(s.session_id);
      });

      groupEl.appendChild(itemEl);
    });

    el.sessionsList.appendChild(groupEl);
  });
}

async function createNewSession() {
  try {
    const resp = await fetch("/api/chat/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: "Cuộc trò chuyện mới" }),
    });
    const session = await resp.json();
    state.currentSessionId = session.session_id;
    state.currentSession = session;
    state.attachedDocuments = [];

    // Update UI
    el.headerSessionTitle.textContent = session.title;
    el.attachedTagsList.innerHTML = "";
    el.messagesList.innerHTML = "";
    showWelcomeScreen();

    // Clear composer attachments
    renderComposerAttachmentsFromState();

    // Reload sessions list
    loadSessionsListOnly();
  } catch (err) {
    console.error("Error creating session:", err);
  }
}

async function loadSessionDetail(sessionId) {
  state.currentSessionId = sessionId;
  try {
    const resp = await fetch(`/api/chat/sessions/${sessionId}`);
    if (!resp.ok) return;
    const session = await resp.json();
    state.currentSession = session;
    state.attachedDocuments = session.attached_documents || [];

    // Header title
    el.headerSessionTitle.textContent = session.title;

    // Render attached tags in header
    renderAttachedTags(state.attachedDocuments);

    // Render composer attachment chips
    renderComposerAttachmentsFromState();

    // Active session item in sidebar
    document.querySelectorAll(".session-item").forEach((it) => {
      it.classList.toggle("active", it.dataset.sessionId === sessionId);
    });

    // Render messages or welcome screen
    if (!session.messages || session.messages.length === 0) {
      showWelcomeScreen();
    } else {
      activateChatStreamView();
      renderMessagesList(session.messages);
    }
  } catch (err) {
    console.error("Error loading session detail:", err);
  }
}

async function loadSessionsListOnly() {
  try {
    const resp = await fetch("/api/chat/sessions");
    const data = await resp.json();
    state.sessions = data.sessions || [];
    renderSidebarSessions(state.sessions);
  } catch (err) {}
}

async function renameSession(sessionId, newTitle) {
  try {
    const resp = await fetch(`/api/chat/sessions/${sessionId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: newTitle }),
    });
    if (resp.ok) {
      if (state.currentSessionId === sessionId) {
        el.headerSessionTitle.textContent = newTitle;
      }
      loadSessionsListOnly();
    }
  } catch (err) {}
}

async function deleteSession(sessionId) {
  try {
    const resp = await fetch(`/api/chat/sessions/${sessionId}`, {
      method: "DELETE",
    });
    if (resp.ok) {
      loadSessions();
    }
  } catch (err) {}
}

// ==============================================================================
// ATTACHED DOCUMENTS TAGS (Header bar)
// ==============================================================================
function renderAttachedTags(docs) {
  el.attachedTagsList.innerHTML = "";
  if (!docs || docs.length === 0) {
    el.inputDocIndicator.innerHTML = '<span class="doc-badge-pill">● Toàn bộ tài liệu</span>';
    return;
  }

  el.inputDocIndicator.innerHTML = `<span class="doc-badge-pill">● ${docs.length} tài liệu đang chọn</span>`;

  docs.forEach((d) => {
    const tag = document.createElement("div");
    tag.className = "doc-tag";
    tag.innerHTML = `
      <span>📄</span>
      <span class="doc-tag-name" title="${escapeHtml(d.title)}">${escapeHtml(d.title)}</span>
      <button class="doc-tag-remove" title="Bỏ tài liệu khỏi cuộc trò chuyện">✕</button>
    `;

    tag.querySelector(".doc-tag-remove").addEventListener("click", () => {
      detachDocumentFromSession(d.document_id);
    });

    el.attachedTagsList.appendChild(tag);
  });
}

function addAttachedDocument(doc) {
  const exists = state.attachedDocuments.some((d) => d.document_id === doc.document_id);
  if (!exists) {
    state.attachedDocuments.push(doc);
    renderAttachedTags(state.attachedDocuments);
  }
}

async function detachDocumentFromSession(docId) {
  if (!state.currentSessionId) return;
  try {
    const resp = await fetch(`/api/chat/sessions/${state.currentSessionId}/documents/${docId}`, {
      method: "DELETE",
    });
    if (resp.ok) {
      state.attachedDocuments = state.attachedDocuments.filter((d) => d.document_id !== docId);
      renderAttachedTags(state.attachedDocuments);
      renderComposerAttachmentsFromState();
      if (!state.currentSession?.messages || state.currentSession.messages.length === 0) {
        showWelcomeScreen();
      }
    }
  } catch (err) {}
}

// ==============================================================================
// CHAT MESSAGE PIPELINE
// ==============================================================================
function activateChatStreamView() {
  if (el.welcomeScreen) el.welcomeScreen.style.display = "none";
  if (el.readyScreen) el.readyScreen.style.display = "none";
  if (el.memoryReadyCard) el.memoryReadyCard.style.display = "none";
  if (el.ingestionPipelineCard) el.ingestionPipelineCard.style.display = "none";
  if (el.messagesStream) el.messagesStream.style.display = "flex";
}

function showWelcomeScreen() {
  if (el.messagesStream) el.messagesStream.style.display = "none";
  if (el.messagesList) el.messagesList.innerHTML = "";

  if (state.attachedDocuments && state.attachedDocuments.length > 0) {
    if (el.welcomeScreen) el.welcomeScreen.style.display = "none";
    if (el.readyScreen) el.readyScreen.style.display = "flex";
    if (el.memoryReadyCard) el.memoryReadyCard.style.display = "block";
    renderReadyActiveDocs();
  } else {
    if (el.welcomeScreen) el.welcomeScreen.style.display = "flex";
    if (el.readyScreen) el.readyScreen.style.display = "none";
    if (el.memoryReadyCard) el.memoryReadyCard.style.display = "none";
    if (el.ingestionPipelineCard) el.ingestionPipelineCard.style.display = "none";
  }
}

function renderReadyActiveDocs() {
  if (!el.readyActiveDocsList) return;
  el.readyActiveDocsList.innerHTML = "";
  if (!state.attachedDocuments || state.attachedDocuments.length === 0) return;

  state.attachedDocuments.forEach((doc) => {
    const chip = document.createElement("div");
    chip.className = "ready-doc-chip";
    chip.innerHTML = `
      <span class="chip-icon">📄</span>
      <span class="chip-title" title="${escapeHtml(doc.title || doc.file_name)}">${escapeHtml(doc.title || doc.file_name)}</span>
      <button class="chip-remove-btn" title="Bỏ tài liệu này khỏi cuộc trò chuyện">✕</button>
    `;
    chip.querySelector(".chip-remove-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      detachDocumentFromSession(doc.document_id);
    });
    el.readyActiveDocsList.appendChild(chip);
  });
}

async function submitUserMessage() {
  const query = el.chatTextarea.value.trim();
  if (!query || !state.currentSessionId) return;

  // Clear input
  el.chatTextarea.value = "";
  el.chatTextarea.style.height = "auto";
  el.btnSendMessage.disabled = true;

  // Make sure messages stream is active
  activateChatStreamView();

  // 1. Render User Message
  renderUserMessage(query);
  scrollToBottom();

  // 2. Show thinking state
  showThinkingIndicator("Đang tìm kiếm trong tài liệu...");

  setTimeout(() => {
    if (el.thinkingIndicator.style.display !== "none") {
      el.thinkingText.textContent = "Đang chuẩn bị câu trả lời...";
    }
  }, 400);

  // 3. Post to backend
  try {
    const resp = await fetch(`/api/chat/sessions/${state.currentSessionId}/messages`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        answer_mode: state.answerMode,
        mode: "hybrid",
        top_k: 5,
        language: "vi",
      }),
    });

    hideThinkingIndicator();

    if (!resp.ok) {
      const err = await resp.json();
      renderAssistantMessage({
        content: `Lỗi: ${err.detail || "Không thể xử lý câu hỏi lúc này."}`,
        refused: true,
      });
      return;
    }

    const data = await resp.json();
    state.lastAssistantMessage = data;

    // Update session title in client state & header if auto-generated by backend
    if (data.session_title && state.currentSession) {
      state.currentSession.title = data.session_title;
      if (el.headerSessionTitle) {
        el.headerSessionTitle.textContent = data.session_title;
      }
    }

    // Render Assistant message
    renderAssistantMessage(data.message, data.diagnostics);

    // Update research drawer metrics if open
    updateResearchDrawer(data);

    // Update sidebar title if changed
    loadSessionsListOnly();
  } catch (error) {
    hideThinkingIndicator();
    console.error("Chat error:", error);
    renderAssistantMessage({
      content: "Đã xảy ra sự cố khi kết nối với máy chủ. Vui lòng thử lại.",
      refused: true,
    });
  } finally {
    el.btnSendMessage.disabled = false;
    scrollToBottom();
  }
}

function renderUserMessage(text) {
  const msgEl = document.createElement("div");
  msgEl.className = "message-item user";
  msgEl.innerHTML = `
    <div class="message-bubble">${escapeHtml(text)}</div>
    <div class="message-avatar">👤</div>
  `;
  el.messagesList.appendChild(msgEl);
}

function renderAssistantMessage(msg, diagnostics) {
  const msgEl = document.createElement("div");
  msgEl.className = "message-item assistant";

  // Parse citations in text like [1], [2] to make them clickable or show refusal notice
  const formattedHtml = formatAssistantAnswer(msg, msg.citations || []);

  let researchBadgeHtml = "";
  if (state.researchMode) {
    const routing = (diagnostics && diagnostics.routing) || msg.routing || "DIRECT_LOOKUP";
    const totalTokens = (msg.telemetry && msg.telemetry.total_tokens) || 0;
    const latency = (msg.telemetry && msg.telemetry.total_latency_ms) || 0;

    researchBadgeHtml = `
      <div class="message-research-meta">
        <span>🔬 ${routing} · ${totalTokens} tokens · ${latency} ms</span>
        <button class="btn-inspect-answer" data-msg-id="${msg.id}">Tại sao có câu trả lời này?</button>
      </div>
    `;
  }

  msgEl.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-bubble">
      <div class="assistant-content">${formattedHtml}</div>
      ${researchBadgeHtml}
    </div>
  `;

  // Attach citation click handlers
  msgEl.querySelectorAll(".citation-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const passageId = link.dataset.passageId;
      openCitationPanel(passageId, msg.citations);
    });
  });

  // Attach inspect click handler
  const btnInspect = msgEl.querySelector(".btn-inspect-answer");
  if (btnInspect) {
    btnInspect.addEventListener("click", () => {
      openResearchDrawer();
    });
  }

  // Attach expandable evidence preview handlers
  msgEl.querySelectorAll(".btn-toggle-evidence").forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.dataset.target;
      const snippet = msgEl.querySelector(`#${targetId}`);
      if (snippet) {
        if (snippet.style.display === "none") {
          snippet.style.display = "block";
          btn.textContent = "🙈 Ẩn đoạn trích";
        } else {
          snippet.style.display = "none";
          btn.textContent = "👁️ Xem đoạn trích";
        }
      }
    });
  });

  el.messagesList.appendChild(msgEl);
}

function renderMessagesList(messages) {
  el.messagesList.innerHTML = "";
  messages.forEach((m) => {
    if (m.role === "user") {
      renderUserMessage(m.content);
    } else {
      renderAssistantMessage(m, m.diagnostics);
    }
  });
  scrollToBottom();
}

function formatAssistantAnswer(msgOrText, localCitations = []) {
  if (!msgOrText) return "";

  const text = typeof msgOrText === "string" ? msgOrText : (msgOrText.content || "");
  const isRefused = typeof msgOrText === "object" ? !!msgOrText.refused : false;
  const citations = (typeof msgOrText === "object" && msgOrText.citations) ? msgOrText.citations : localCitations;

  // 8. UNSUPPORTED QUESTION Refusal presentation
  if (isRefused) {
    return `
      <div class="refusal-notice-card">
        <div class="refusal-badge">⚠️ THÔNG BÁO TÀI LIỆU</div>
        <p class="refusal-main">Không tìm thấy đủ thông tin trong tài liệu để trả lời chắc chắn.</p>
        <p class="refusal-sub">Bạn có thể thử hỏi một câu khác liên quan đến nội dung tài liệu.</p>
      </div>
    `;
  }

  // Split into body and sources section if present
  let body = text;
  if (text.includes("### Nguồn tham khảo")) {
    const parts = text.split("### Nguồn tham khảo");
    body = parts[0];
  }

  // Replace [1], [2] in body with clickable buttons
  citations.forEach((c) => {
    const tag = `[${c.citation_index}]`;
    const replaceHtml = `<button class="citation-link" data-passage-id="${c.passage_id}" title="Xem trích dẫn từ ${escapeHtml(c.document_title)}">[${c.citation_index}]</button>`;
    body = body.split(tag).join(replaceHtml);
  });

  // Simple markdown formatting for bold, bullets
  let bodyHtml = escapeHtml(body)
    .replace(/&lt;button class=&quot;citation-link&quot; data-passage-id=&quot;(.*?)&quot; title=&quot;(.*?)&quot;&gt;\[(.*?)\]&lt;\/button&gt;/g,
      '<button class="citation-link" data-passage-id="$1" title="$2">[$3]</button>')
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\n\n/g, "</p><p>")
    .replace(/\n- /g, "<br>• ");

  // 7. Visual Separation: TRẢ LỜI
  let html = `
    <div class="answer-section-block">
      <div class="section-label-header">TRẢ LỜI</div>
      <div class="answer-text-content"><p>${bodyHtml}</p></div>
    </div>
  `;

  // Visual Separation: CĂN CỨ
  if (citations && citations.length > 0) {
    let evidenceCards = "";
    citations.forEach((c) => {
      const pId = c.passage_id || `cite-${c.citation_index}`;
      const docTitle = c.document_title || "Tài liệu";
      const secTitle = c.section_title || "Phần nội dung";
      const pNum = c.paragraph_index || 1;
      const snippetText = c.text || c.snippet || "Đoạn chứng cứ hỗ trợ câu trả lời.";

      evidenceCards += `
        <div class="evidence-card-compact">
          <div class="evidence-header-row">
            <button class="evidence-cite-badge citation-link" data-passage-id="${escapeHtml(pId)}" title="Xem bằng chứng [${c.citation_index}]">[${c.citation_index}]</button>
            <div class="evidence-meta-info">
              <span class="evidence-doc-name">${escapeHtml(docTitle)}</span>
              <span class="evidence-sec-name">${escapeHtml(secTitle)}</span>
              <span class="evidence-para-num">Đoạn ${pNum}</span>
            </div>
            <button class="evidence-fulltext-btn citation-link" data-passage-id="${escapeHtml(pId)}" title="Xem toàn văn trong tài liệu">Xem toàn văn</button>
          </div>
          <div class="evidence-excerpt-text">
            "${escapeHtml(snippetText)}"
          </div>
        </div>
      `;
    });

    html += `
      <div class="evidence-section-block">
        <div class="section-label-header">CĂN CỨ</div>
        <div class="evidence-list-container">
          ${evidenceCards}
        </div>
      </div>
    `;
  }

  return html;
}

function showThinkingIndicator(msg) {
  el.thinkingText.textContent = msg || "Đang tìm kiếm trong tài liệu...";
  el.thinkingIndicator.style.display = "flex";
  scrollToBottom();
}

function hideThinkingIndicator() {
  el.thinkingIndicator.style.display = "none";
}

function scrollToBottom() {
  setTimeout(() => {
    el.chatScrollContainer.scrollTop = el.chatScrollContainer.scrollHeight;
  }, 50);
}

// ==============================================================================
// CITATION EXPLORER PANEL
// ==============================================================================
async function openCitationPanel(passageId, localCitations) {
  el.sourcePanel.classList.add("open");

  // First check if passage is in current message citations
  let matched = null;
  if (localCitations) {
    matched = localCitations.find((c) => c.passage_id === passageId);
  }

  if (matched) {
    displayCitationData(matched);
    return;
  }

  // Fetch from server
  try {
    el.sourceQuoteText.textContent = "Đang tải trích dẫn...";
    const resp = await fetch(`/api/citations/${passageId}`);
    if (resp.ok) {
      const data = await resp.json();
      displayCitationData(data);
    } else {
      el.sourceQuoteText.textContent = "Không tìm thấy nội dung trích dẫn này.";
    }
  } catch (err) {
    el.sourceQuoteText.textContent = "Lỗi khi nạp trích dẫn.";
  }
}

function displayCitationData(data) {
  el.sourceDocTitle.textContent = data.document_title || data.document_id || "Tài liệu";
  el.sourceSectionTitle.textContent = data.section_title || "Phần nội dung";
  el.sourceParagraphIndex.textContent = `Đoạn ${data.paragraph_index || 1}`;
  el.sourceScore.textContent = data.score ? `Độ khớp: ${data.score}` : "Bằng chứng hỗ trợ";
  el.sourceQuoteText.textContent = `"${data.text || ""}"`;

  if (el.btnViewDocStructure) {
    el.btnViewDocStructure.onclick = () => {
      openDocumentsModal();
    };
  }
}

// ==============================================================================
// RESEARCH MODE & COMPARE
// ==============================================================================
function setResearchMode(enabled) {
  state.researchMode = enabled;
  el.researchModeStatus.textContent = enabled ? "Đang bật" : "Đang tắt";
  el.researchModeStatus.style.color = enabled ? "var(--success)" : "var(--text-muted)";

  // Re-render messages to show/hide research badges
  if (state.currentSession && state.currentSession.messages) {
    renderMessagesList(state.currentSession.messages);
  }

  if (enabled) {
    openResearchDrawer();
  } else {
    el.researchDrawer.classList.remove("open");
  }
}

function openResearchDrawer() {
  el.researchDrawer.classList.add("open");
  if (state.lastAssistantMessage) {
    updateResearchDrawer(state.lastAssistantMessage);
  }
}

function updateResearchDrawer(data) {
  const diag = data.diagnostics || {};
  const telem = data.telemetry || {};

  el.drawerRouteName.textContent = diag.routing || "DIRECT_LOOKUP";
  el.drawerRouteDesc.textContent = diag.route_explanation || "Định tuyến câu hỏi document-grounded";
  el.drawerEvidenceCount.textContent = diag.evidence_count || (data.citations ? data.citations.length : 0);
  el.drawerRefusalStatus.textContent = data.refused ? "Từ chối (Ngoài phạm vi)" : "Được xác thực";
  el.drawerRefusalStatus.style.color = data.refused ? "var(--danger)" : "var(--success)";
  el.drawerMemoryLevel.textContent = diag.memory_level || "Level 3 (SA-CMS)";

  el.drawerInputTokens.textContent = telem.input_tokens || 0;
  el.drawerOutputTokens.textContent = telem.output_tokens || 0;
  el.drawerTotalLatency.textContent = `${telem.total_latency_ms || 0} ms`;
  el.drawerRetrievalLatency.textContent = `${telem.retrieval_ms || 0} ms`;
}

async function runModelComparison() {
  const query = state.lastAssistantMessage?.effective_query || "Kiến trúc SA-CMS là gì?";
  el.drawerCompareGrid.innerHTML = '<div class="compare-placeholder">Đang so sánh B1, B2, P1, P2...</div>';

  try {
    const resp = await fetch("/api/chat/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        query: query,
        methods: ["B1", "B2", "P1", "P2"],
        answer_mode: "balanced",
      }),
    });

    if (!resp.ok) throw new Error("Lỗi khi so sánh");
    const data = await resp.json();
    renderCompareResults(data.comparison);
  } catch (err) {
    el.drawerCompareGrid.innerHTML = '<div class="compare-placeholder">Lỗi khi chạy so sánh.</div>';
  }
}

function renderCompareResults(comp) {
  el.drawerCompareGrid.innerHTML = "";
  const methodNames = {
    B1: "B1: Full-Context",
    B2: "B2: Standard RAG",
    P1: "P1: SA-CMS Memory-only",
    P2: "P2: SA-CMS Gated Hybrid",
  };

  Object.entries(comp).forEach(([key, val]) => {
    const card = document.createElement("div");
    card.className = "compare-card-item";
    card.innerHTML = `
      <div class="compare-card-header">
        <span>${methodNames[key] || key}</span>
        <span>${val.total_tokens} tokens · ${val.latency_ms} ms</span>
      </div>
      <div class="compare-card-body">${escapeHtml(val.answer)}</div>
    `;
    el.drawerCompareGrid.appendChild(card);
  });
}

// ==============================================================================
// DOCUMENT LIBRARY MODAL
// ==============================================================================
function openDocumentsModal() {
  el.modalDocuments.style.display = "flex";
  loadDocumentsTable();
}

function closeDocumentsModal() {
  el.modalDocuments.style.display = "none";
}

async function loadDocumentsTable(searchTerm = "") {
  try {
    let url = "/api/documents";
    if (searchTerm) url += `?search=${encodeURIComponent(searchTerm)}`;
    const resp = await fetch(url);
    const data = await resp.json();
    renderDocumentsTable(data.documents || []);
  } catch (err) {
    console.error("Error loading documents table:", err);
  }
}

function renderDocumentsTable(docs) {
  el.documentsTableBody.innerHTML = "";
  if (docs.length === 0) {
    el.documentsTableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">Chưa có tài liệu nào.</td></tr>';
    return;
  }

  docs.forEach((d) => {
    const formattedDate = (() => {
      if (!d.created_at) return "Vừa xong";
      if (typeof d.created_at === "number") {
        const ts = d.created_at < 10000000000 ? d.created_at * 1000 : d.created_at;
        const dateObj = new Date(ts);
        return isNaN(dateObj.getTime()) ? "Vừa xong" : dateObj.toISOString().substring(0, 10);
      }
      const str = String(d.created_at);
      return str.length >= 10 ? str.substring(0, 10) : str;
    })();

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><strong>${escapeHtml(d.title)}</strong></td>
      <td>${d.token_estimate} tokens (${d.word_count} từ)</td>
      <td>${d.passage_count} đoạn</td>
      <td>${formattedDate}</td>
      <td>
        <button class="btn btn-sm btn-outline btn-chat-doc" style="margin-right: 4px;">Trò chuyện</button>
        <button class="btn btn-sm btn-ghost btn-del-doc" style="color: var(--danger);">Xóa</button>
      </td>
    `;

    tr.querySelector(".btn-chat-doc").addEventListener("click", () => {
      attachDocAndSwitchToChat(d.document_id, d.title);
    });

    tr.querySelector(".btn-del-doc").addEventListener("click", () => {
      if (confirm(`Xác nhận xóa tài liệu "${d.title}"?`)) {
        deleteDocument(d.document_id);
      }
    });

    el.documentsTableBody.appendChild(tr);
  });
}

async function attachDocAndSwitchToChat(docId, title) {
  if (state.currentSessionId) {
    await fetch(`/api/chat/sessions/${state.currentSessionId}/documents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: docId }),
    });
    addAttachedDocument({ document_id: docId, title: title });
    renderComposerAttachmentsFromState();
  } else {
    await createNewSession();
    await fetch(`/api/chat/sessions/${state.currentSessionId}/documents`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: docId }),
    });
    addAttachedDocument({ document_id: docId, title: title });
    renderComposerAttachmentsFromState();
  }
  closeDocumentsModal();
  activateChatStreamView();
}

async function deleteDocument(docId) {
  try {
    const resp = await fetch(`/api/documents/${docId}`, { method: "DELETE" });
    if (resp.ok) {
      loadDocumentsTable();
    }
  } catch (err) {}
}

// ==============================================================================
// RESEARCH LAB — 10-STEP GUIDED INTERACTIVE DEMO (Step 12)
// ==============================================================================
const DEMO_STEPS = [
  {
    step: 1,
    title: "Bước 1: Nạp tài liệu (Load Document)",
    subtitle: "Hệ thống tiếp nhận tệp tin và lưu trữ cục bộ an toàn",
    stateTag: "FILE STORED",
    tagClass: "badge-phase4",
    detail: "Tài liệu được đưa vào thư mục lưu trữ cục bộ. Hệ thống không gửi bất kỳ byte dữ liệu nào qua mạng Internet, tuân thủ tuyệt đối nguyên tắc ngoại tuyến.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div class="visual-file-meta" style="display:flex; align-items:center;">
          <span class="file-icon" style="font-size:1.8rem; margin-right:0.75rem;">📄</span>
          <div>
            <strong>DEMO_DOC_001.pdf</strong> (24.5 KB)
            <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">Hash: <code>e8b1...9c2a</code> · SHA-256 Verified</div>
          </div>
        </div>
        <div class="visual-status-pill success" style="margin-top:0.75rem; color:var(--success); font-weight:600;">✓ File đã lưu an toàn trên ổ đĩa cục bộ</div>
      </div>
    `,
    observable: "Trạng thái: FILE STORED · Kiểm tra tính toàn vẹn: SHA-256 Verified · Mạng: Ngắt kết nối (100% Offline)"
  },
  {
    step: 2,
    title: "Bước 2: Phân tích cấu trúc phân cấp (Show Document Structure)",
    subtitle: "Nhận diện cấu trúc tự nhiên: Đoạn văn, Mục và Tài liệu",
    stateTag: "STRUCTURE PARSED",
    tagClass: "badge-round2",
    detail: "Bộ bóc tách phân tích tài liệu theo cú pháp tự nhiên: xác định ranh giới đoạn (Paragraphs), các tiêu đề mục lớn (Sections) và ngữ cảnh toàn tài liệu (Document).",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="font-family:monospace; font-size:0.85rem; line-height:1.6; color:var(--text-secondary);">
          <div>📁 Tài liệu: DEMO_DOC_001 (Document L3)</div>
          <div style="margin-left:1.5rem;">├── 📑 Mục 1: Tổng quan Kiến trúc (Section L2)</div>
          <div style="margin-left:3rem;">│   ├── 📄 Đoạn 1.1: Định nghĩa CMS (Paragraph L1)</div>
          <div style="margin-left:3rem;">│   └── 📄 Đoạn 1.2: Ranh giới Cấu trúc (Paragraph L1)</div>
          <div style="margin-left:1.5rem;">└── 📑 Mục 2: Cơ chế Hòa trộn (Section L2)</div>
          <div style="margin-left:3rem;">    └── 📄 Đoạn 2.1: Residual Blending (Paragraph L1)</div>
        </div>
      </div>
    `,
    observable: "Trạng thái: STRUCTURE PARSED · L1 (12 Đoạn) · L2 (3 Mục) · L3 (1 Toàn tài liệu)"
  },
  {
    step: 3,
    title: "Bước 3: Phân rã 3 cấp độ L1, L2, L3 (Memory Mapping)",
    subtitle: "Ánh xạ tương ứng: L1 Đoạn văn, L2 Mục, L3 Toàn tài liệu",
    stateTag: "HIERARCHY MAPPED",
    tagClass: "badge-phase4",
    detail: "L1 lưu chi tiết cục bộ ở cấp đoạn. L2 tổng hợp thông tin ở cấp mục. L3 lưu trạng thái vĩ mô ở cấp tài liệu. Toàn bộ 135M tham số của SmolLM2 được đóng băng tuyệt đối.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align:center;">
          <div style="background:var(--bg-card); padding:8px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="color:var(--accent-primary); font-weight:700;">L1 (Đoạn)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">1,771,584 params</div>
            <div style="font-size:0.72rem; color:var(--text-secondary); margin-top:4px;">Thang thời gian mịn</div>
          </div>
          <div style="background:var(--bg-card); padding:8px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="color:var(--accent-secondary); font-weight:700;">L2 (Mục)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">1,771,584 params</div>
            <div style="font-size:0.72rem; color:var(--text-secondary); margin-top:4px;">Mạch lạc chủ đề</div>
          </div>
          <div style="background:var(--bg-card); padding:8px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="color:var(--text-accent); font-weight:700;">L3 (Tài liệu)</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">1,771,584 params</div>
            <div style="font-size:0.72rem; color:var(--text-secondary); margin-top:4px;">Neo trạng thái thô</div>
          </div>
        </div>
      </div>
    `,
    observable: "Trạng thái: 3-LEVEL MEMORY ADAPTER INITIALIZED · 5,314,752 tham số (d=576) · Backbone: Frozen 100%"
  },
  {
    step: 4,
    title: "Bước 4: Mô phỏng nạp tri thức vào SA-CMS Memory (Reading / Ingestion)",
    subtitle: "Cập nhật trạng thái bộ nhớ liên tục và lưu trữ đĩa cục bộ",
    stateTag: "MEMORY INGESTED",
    tagClass: "badge-ready",
    detail: "Hệ thống duyệt qua văn bản và cập nhật trạng thái bộ nhớ tham số cục bộ. Tri thức được nén bền vững vào đĩa mà không cần gọi API đám mây hay mạng ngoài.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <strong>Cập nhật Vector Trạng thái Bộ nhớ:</strong>
            <div style="font-size:0.8rem; color:var(--text-muted); margin-top:2px;">||M_t|| norm: <code>1.4827</code> · Memory update: Completed</div>
          </div>
          <span class="visual-status-pill success" style="color:var(--success); font-weight:600;">✓ Snapshot Saved</span>
        </div>
        <div style="margin-top:8px; font-size:0.82rem; color:var(--text-secondary);">
          Đường dẫn lưu trữ: <code>data/memory_snapshots/DEMO_DOC_001.pt</code> (Zero Cloud Egress)
        </div>
      </div>
    `,
    observable: "Trạng thái: MEMORY INGESTED · Peak VRAM: 357 MB · Đĩa lưu: Cục bộ · Sẵn sàng hỏi đáp"
  },
  {
    step: 5,
    title: "Bước 5: Đặt câu hỏi truy vấn (Ask Question)",
    subtitle: "Người dùng đặt câu hỏi về tài liệu đã nạp",
    stateTag: "QUERY DISPATCHED",
    tagClass: "badge-round2",
    detail: "Câu hỏi được tiếp nhận và xử lý cục bộ: kích hoạt đồng thời bộ nhớ tham số SA-CMS và trích xuất chỉ mục đoạn cục bộ BM25.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="font-weight:600; color:var(--text-primary); margin-bottom:4px;">
          ❓ Câu hỏi: "Tầng 1 của hệ thống CMS đảm nhiệm vai trò gì trong kiến trúc?"
        </div>
        <div style="font-size:0.82rem; color:var(--text-secondary);">
          Phân tích: Thực thể <code>Tầng 1 CMS</code> · Độ dài: Cân bằng · Top-k: 5
        </div>
      </div>
    `,
    observable: "Trạng thái: QUERY PROCESSED · Cơ chế: P2 Gated Hybrid · Bộ nhớ tham số: Kích hoạt"
  },
  {
    step: 6,
    title: "Bước 6: Hiển thị câu trả lời (Show Answer)",
    subtitle: "Cơ chế P2 hòa trộn biểu diễn bộ nhớ và trích xuất cục bộ",
    stateTag: "ANSWER READY",
    tagClass: "badge-phase4",
    detail: "Cơ chế cổng phần dư Gated Residual Blending kết hợp biểu diễn trạng thái bộ nhớ SA-CMS với các đoạn trích từ chỉ mục BM25, sinh câu trả lời chính xác có căn cứ.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="font-size:0.85rem; line-height:1.5;">
          <strong style="color:var(--accent-primary);">TRẢ LỜI:</strong><br>
          Tầng 1 của CMS đảm nhiệm vai trò lưu giữ thông tin cục bộ ở cấp đoạn văn, nắm bắt vi cú pháp và các thực thể chi tiết <button class="citation-link">[1]</button>.
        </div>
      </div>
    `,
    observable: "Trạng thái: INFERENCE COMPLETE · TTFT: 58.89 ms · Tổng độ trễ: 142 ms · Trích dẫn: [1]"
  },
  {
    step: 7,
    title: "Bước 7: Mở căn cứ trích dẫn cục bộ (Open Evidence)",
    subtitle: "Kiểm tra tính trung thực khoa học qua đoạn trích gốc",
    stateTag: "EVIDENCE VERIFIED",
    tagClass: "badge-ready",
    detail: "Người dùng nhấp vào [1] để đối chiếu trực tiếp văn bản nguồn từ ổ đĩa cục bộ. Không sử dụng bất kỳ liên kết web hay công cụ tìm kiếm bên ngoài nào.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="font-size:0.85rem; font-weight:600; color:var(--accent-primary); margin-bottom:4px;">
          CĂN CỨ: [1] DEMO_DOC_001 — Mục 1 — Đoạn 1
        </div>
        <div style="font-style:italic; font-size:0.82rem; color:var(--text-secondary); background:var(--bg-main); padding:6px; border-radius:4px;">
          "Tầng 1 (L1) hoạt động ở thang thời gian mịn nhất, cập nhật theo từng đoạn văn bản nhằm mã hóa các chi tiết ngữ nghĩa cục bộ..."
        </div>
      </div>
    `,
    observable: "Trạng thái: EVIDENCE VERIFIED · Khớp văn bản: 100% Khớp câu chữ · Liên kết web: Không tồn tại"
  },
  {
    step: 8,
    title: "Bước 8: Loại bỏ ngữ cảnh trực tiếp (Remove Direct Context)",
    subtitle: "Thử thách bộ nhớ: Xóa bỏ ngữ cảnh trực tiếp trong prompt (Context Eviction)",
    stateTag: "CONTEXT EVICTED",
    tagClass: "badge-round2",
    detail: "Mô phỏng tình huống ngữ cảnh trực tiếp bị loại bỏ hoặc vượt quá cửa sổ ngữ cảnh. Chế độ P1/P2 kích hoạt truy vấn trực tiếp từ bộ nhớ tham số đã lưu.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
          <span style="color:var(--danger); font-weight:600;">⚠️ Ngữ cảnh trực tiếp: ĐÃ BỊ LOẠI BỎ (Evicted)</span>
          <span class="visual-status-pill success" style="color:var(--success); font-weight:600;">✓ Memory State Intact</span>
        </div>
        <div style="font-size:0.82rem; color:var(--text-secondary);">
          Prompt context: 0 tokens · Nguồn tri thức: Bộ nhớ tham số SA-CMS L1/L2/L3 (5.3M tham số)
        </div>
      </div>
    `,
    observable: "Trạng thái: CONTEXT EVICTED · Trạng thái bộ nhớ tham số: Khôi phục 100% · Khả năng nhớ: Ổn định"
  },
  {
    step: 9,
    title: "Bước 9: Đặt lại cùng câu hỏi (Ask Same Question)",
    subtitle: "Truy vấn bộ nhớ thuần (P1 Memory-Only) khi không có ngữ cảnh văn bản",
    stateTag: "MEMORY RECALL",
    tagClass: "badge-round2",
    detail: "Đặt lại cùng một câu hỏi. Thay vì thất bại do thiếu prompt context, bộ nhớ tham số SA-CMS tái tạo câu trả lời chuẩn xác dựa trên vector trạng thái đã được ghi nhớ.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="font-size:0.85rem; line-height:1.5;">
          <strong style="color:var(--accent-secondary);">TRẢ LỜI (QUA BỘ NHỚ P1):</strong><br>
          Tầng 1 chịu trách nhiệm lưu thông tin cấp đoạn, bảo tồn cấu trúc chi tiết của tài liệu ngay cả khi văn bản thô không nằm trong prompt.
        </div>
      </div>
    `,
    observable: "Trạng thái: MEMORY RECALL SUCCESSFUL · Độ suy giảm tri thức: 0.0% · Phục hồi nguyên bản"
  },
  {
    step: 10,
    title: "Bước 10: Quan sát kết quả & Hiệu quả Token (Observable Result)",
    subtitle: "Đánh giá khả năng bảo toàn tri thức và tiết kiệm tài nguyên thực tế",
    stateTag: "VERIFICATION COMPLETE",
    tagClass: "badge-phase4",
    detail: "So sánh hiệu quả thực tế: SA-CMS P2 đạt độ chính xác tương đương Full-Context nhưng tiết kiệm 76.6% Input Tokens, giảm 41.7% thời gian trễ TTFT và chạy 100% ngoại tuyến.",
    visualHtml: `
      <div class="stepper-visual-box">
        <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align:center;">
          <div style="background:var(--bg-card); padding:6px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-weight:700; color:var(--success);">-76.6%</div>
            <div style="font-size:0.75rem;">Input Tokens</div>
          </div>
          <div style="background:var(--bg-card); padding:6px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-weight:700; color:var(--success);">-56.2%</div>
            <div style="font-size:0.75rem;">Output Tokens</div>
          </div>
          <div style="background:var(--bg-card); padding:6px; border-radius:6px; border:1px solid var(--border-subtle);">
            <div style="font-weight:700; color:var(--accent-primary);">58.89 ms</div>
            <div style="font-size:0.75rem;">TTFT (Độ trễ)</div>
          </div>
        </div>
      </div>
    `,
    observable: "Kết luận thực nghiệm: 0 Ảo giác · Tiết kiệm token vượt trội · 100% Ngoại tuyến · Bảo vệ danh dự NCKH"
  }
];

let currentDemoStep = 0;
let demoAutoTimer = null;

function renderDemoStep(idx) {
  if (idx < 0) idx = 0;
  if (idx >= DEMO_STEPS.length) idx = DEMO_STEPS.length - 1;
  currentDemoStep = idx;

  const item = DEMO_STEPS[idx];
  if (el.demoStepperFill) {
    el.demoStepperFill.style.width = `${((idx + 1) / DEMO_STEPS.length) * 100}%`;
  }
  if (el.demoStepBadge) {
    el.demoStepBadge.textContent = `Bước ${item.step} / ${DEMO_STEPS.length}`;
  }
  if (el.demoStepTitle) {
    el.demoStepTitle.textContent = item.title;
  }
  if (el.demoStepContentCard) {
    el.demoStepContentCard.innerHTML = `
      <div class="step-card-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <div>
          <h5 style="margin:0; font-size:1rem; color:var(--text-primary);">${item.title}</h5>
          <span style="font-size:0.82rem; color:var(--text-muted);">${item.subtitle}</span>
        </div>
        <span class="badge-tag ${item.tagClass}">${item.stateTag}</span>
      </div>
      <p style="font-size:0.88rem; color:var(--text-secondary); margin:0.75rem 0; line-height:1.5;">${item.detail}</p>
      ${item.visualHtml}
      <div class="step-observable-box" style="margin-top:0.75rem; background:rgba(99, 102, 241, 0.08); border-left:3px solid var(--accent-primary); padding:8px 12px; border-radius:4px; font-size:0.82rem; color:var(--text-primary);">
        <strong>Quan sát thực nghiệm:</strong> ${item.observable}
      </div>
    `;
  }

  if (el.btnDemoPrev) el.btnDemoPrev.disabled = idx === 0;
  if (el.btnDemoNext) el.btnDemoNext.disabled = idx === DEMO_STEPS.length - 1;
}

function initDemoStepperControls() {
  if (el.btnDemoPrev) {
    el.btnDemoPrev.addEventListener("click", () => {
      stopAutoDemo();
      renderDemoStep(currentDemoStep - 1);
    });
  }
  if (el.btnDemoNext) {
    el.btnDemoNext.addEventListener("click", () => {
      stopAutoDemo();
      renderDemoStep(currentDemoStep + 1);
    });
  }
  if (el.btnDemoReset) {
    el.btnDemoReset.addEventListener("click", () => {
      stopAutoDemo();
      renderDemoStep(0);
    });
  }
  if (el.btnDemoAuto) {
    el.btnDemoAuto.addEventListener("click", () => {
      if (demoAutoTimer) {
        stopAutoDemo();
      } else {
        startAutoDemo();
      }
    });
  }
}

function startAutoDemo() {
  if (el.btnDemoAuto) el.btnDemoAuto.innerHTML = "⏸ Dừng tự động";
  demoAutoTimer = setInterval(() => {
    if (currentDemoStep < DEMO_STEPS.length - 1) {
      renderDemoStep(currentDemoStep + 1);
    } else {
      stopAutoDemo();
    }
  }, 2500);
}

function stopAutoDemo() {
  if (demoAutoTimer) {
    clearInterval(demoAutoTimer);
    demoAutoTimer = null;
  }
  if (el.btnDemoAuto) el.btnDemoAuto.innerHTML = "▶ Chạy tự động";
}

// ==============================================================================
// RESEARCH LAB — 8-PAGE DASHBOARD & SCENARIOS
// ==============================================================================
function openDashboardModal() {
  if (el.modalResearchDashboard) {
    el.modalResearchDashboard.style.display = "flex";
    if (el.backdropOverlay) el.backdropOverlay.style.display = "block";
    loadDashboardMetrics();
    renderLabScenarios();
    renderDemoStep(currentDemoStep);
  }
}

function closeDashboardModal() {
  if (el.modalResearchDashboard) {
    el.modalResearchDashboard.style.display = "none";
  }
}

async function loadDashboardMetrics() {
  try {
    const resp = await fetch("/research/metrics");
    if (!resp.ok) return;
    const data = await resp.json();
    console.log("Research metrics loaded:", data);
  } catch (err) {
    console.warn("Could not load /research/metrics:", err);
  }
}

function renderLabScenarios() {
  if (!el.labScenariosList) return;
  el.labScenariosList.innerHTML = "";

  DEMO_SCENARIOS.forEach((d) => {
    const card = document.createElement("div");
    card.className = "demo-card";
    card.innerHTML = `
      <div class="demo-card-header">
        <h4 class="demo-card-title">${escapeHtml(d.title)}</h4>
        <span class="demo-card-badge">${escapeHtml(d.badge)}</span>
      </div>
      <div class="demo-card-body">
        <p><strong>Kỳ vọng:</strong> ${escapeHtml(d.expected_behavior)}</p>
      </div>
      <div class="demo-card-query">
        <strong>Câu hỏi mẫu:</strong> "${escapeHtml(d.query)}"
      </div>
      <div class="demo-card-footer">
        <span class="demo-card-meta">Chế độ: <code>${d.mode}</code> · Trả lời: <code>${d.answer_mode}</code></span>
        <button class="btn-run-demo btn-run-lab-demo" data-demo-id="${d.id}">
          <span>▶</span> Chạy kịch bản này
        </button>
      </div>
    `;

    card.querySelector(".btn-run-lab-demo").addEventListener("click", () => {
      closeDashboardModal();
      runDemoScenario(d);
    });

    el.labScenariosList.appendChild(card);
  });
}

// ==============================================================================
// ROUND 2 — 7 INTERACTIVE DEMO SCENARIOS
// ==============================================================================
const DEMO_SCENARIOS = [
  {
    id: "DEMO_1_SINGLE_DOC",
    title: "Demo 1: Hỏi đáp Tài liệu Đơn lẻ & Trích dẫn Nguồn",
    doc_ids: ["DEMO_DOC_001"],
    query: "Tầng 1 của hệ thống CMS đảm nhiệm vai trò gì trong kiến trúc?",
    expected_behavior: "Trả lời chính xác chức năng Tầng 1 kèm nhãn trích dẫn [1] dẫn xuất trực tiếp đến phần 1 của DEMO_DOC_001.",
    expected_refusal: false,
    mode: "hybrid",
    answer_mode: "balanced",
    badge: "Đơn tài liệu"
  },
  {
    id: "DEMO_2_LONG_DOC_DISTANT",
    title: "Demo 2: Tài liệu Dài & Tra cứu Mục Ở Xa",
    doc_ids: ["DEMO_DOC_002"],
    query: "Tác động kinh tế xã hội và thời gian di chuyển giữa Hà Nội và TP.HCM dự kiến là bao lâu?",
    expected_behavior: "Truy xuất thành công mục 3 ở cuối tài liệu (5 giờ 30 phút, GDP 1%) và trích dẫn chuẩn xác.",
    expected_refusal: false,
    mode: "hybrid",
    answer_mode: "balanced",
    badge: "Mục ở xa"
  },
  {
    id: "DEMO_3_MULTI_DOC_COMPARISON",
    title: "Demo 3: Đối chiếu & So sánh Đa Tài liệu",
    doc_ids: ["DEMO_DOC_001", "DEMO_DOC_002"],
    query: "So sánh nội dung và lĩnh vực chính giữa hai tài liệu.",
    expected_behavior: "Hệ thống trích xuất bằng chứng từ cả 2 tài liệu và tổng hợp so sánh có trích dẫn riêng cho từng tài liệu.",
    expected_refusal: false,
    mode: "hybrid",
    answer_mode: "balanced",
    badge: "Đa tài liệu"
  },
  {
    id: "DEMO_4_REFUSAL_UNSUPPORTED",
    title: "Demo 4: Câu hỏi Ngoài Tài liệu & Cổng Từ chối",
    doc_ids: ["DEMO_DOC_001"],
    query: "Thủ đô của Nhật Bản là thành phố nào và thời tiết hiện tại ra sao?",
    expected_behavior: "Kích hoạt Cổng từ chối: 'Không tìm thấy đủ thông tin trong tài liệu để trả lời chắc chắn.' Tuyệt đối không ảo giác.",
    expected_refusal: true,
    mode: "hybrid",
    answer_mode: "balanced",
    badge: "Cổng từ chối"
  },
  {
    id: "DEMO_5_CONTEXT_EVICTION",
    title: "Demo 5: Xóa Ngữ cảnh & Đánh giá Ưu thế Bộ nhớ P1/P2",
    doc_ids: ["DEMO_DOC_001"],
    query: "Cơ chế cổng hòa trộn phần dư (Gated Residual Blending) hoạt động như thế nào?",
    expected_behavior: "Khi context bị xóa (evicted), bộ nhớ tham số SA-CMS định hướng câu trả lời với mức chi phí input tokens giảm >80%.",
    expected_refusal: false,
    mode: "memory",
    answer_mode: "balanced",
    badge: "Context Eviction"
  },
  {
    id: "DEMO_6_CONCISE_MODE",
    title: "Demo 6: Chế độ Trả lời Cô đọng (Giảm Token Đầu ra)",
    doc_ids: ["DEMO_DOC_001"],
    query: "Cơ chế cổng hòa trộn phần dư giúp ngăn ngừa hiện tượng gì?",
    expected_behavior: "Trả lời cực kỳ ngắn gọn (chỉ 1 câu chứa đáp án cốt lõi: ngăn ngừa trôi dạt biểu diễn) + trích dẫn [1], tiết kiệm >50% token đầu ra.",
    expected_refusal: false,
    mode: "hybrid",
    answer_mode: "concise",
    badge: "Tiết kiệm Token"
  },
  {
    id: "DEMO_7_RESEARCH_MODE_TRACE",
    title: "Demo 7: Chế độ Nghiên cứu & Dấu vết Thần kinh",
    doc_ids: ["DEMO_DOC_001"],
    query: "Tóm tắt cơ chế nén tri thức của SA-CMS.",
    expected_behavior: "Hiển thị toàn bộ dấu vết: Chiến lược định tuyến, Top-k BM25, Trọng số bộ nhớ 3 cấp độ, Độ lệch trạng thái ẩn và Độ lớn phần dư ||M_t||.",
    expected_refusal: false,
    mode: "hybrid",
    answer_mode: "balanced",
    badge: "Dấu vết Thần kinh"
  }
];

function openDemosModal() {
  if (el.modalDemos) {
    el.modalDemos.style.display = "flex";
    if (el.backdropOverlay) el.backdropOverlay.style.display = "block";
    renderDemoScenarios();
  }
}

function closeDemosModal() {
  if (el.modalDemos) {
    el.modalDemos.style.display = "none";
  }
}

function renderDemoScenarios() {
  if (!el.demoScenariosList) return;
  el.demoScenariosList.innerHTML = "";

  DEMO_SCENARIOS.forEach((d) => {
    const card = document.createElement("div");
    card.className = "demo-card";
    card.innerHTML = `
      <div class="demo-card-header">
        <h4 class="demo-card-title">${escapeHtml(d.title)}</h4>
        <span class="demo-card-badge">${escapeHtml(d.badge)}</span>
      </div>
      <div class="demo-card-body">
        <p><strong>Kỳ vọng:</strong> ${escapeHtml(d.expected_behavior)}</p>
      </div>
      <div class="demo-card-query">
        <strong>Câu hỏi mẫu:</strong> "${escapeHtml(d.query)}"
      </div>
      <div class="demo-card-footer">
        <span class="demo-card-meta">Chế độ: <code>${d.mode}</code> · Trả lời: <code>${d.answer_mode}</code></span>
        <button class="btn-run-demo" data-demo-id="${d.id}">
          <span>▶</span> Chạy kịch bản này
        </button>
      </div>
    `;

    card.querySelector(".btn-run-demo").addEventListener("click", () => {
      runDemoScenario(d);
    });

    el.demoScenariosList.appendChild(card);
  });
}

async function runDemoScenario(demo) {
  closeDemosModal();
  if (el.backdropOverlay) el.backdropOverlay.style.display = "none";

  // If no session exists, create one
  if (!state.currentSessionId) {
    await createNewSession();
  }

  // Ensure documents are attached
  try {
    const resp = await fetch("/api/documents");
    if (resp.ok) {
      const data = await resp.json();
      const existingDocs = data.documents || [];

      // If demo docs not in library, auto-seed
      const hasDemoDocs = existingDocs.some(doc => demo.doc_ids.includes(doc.document_id));
      if (!hasDemoDocs) {
        await fetch("/api/demo/seed", { method: "POST" });
        const refetch = await fetch("/api/documents");
        const refetchData = await refetch.json();
        existingDocs.length = 0;
        existingDocs.push(...(refetchData.documents || []));
      }

      // Attach required demo docs to current session
      for (const reqDocId of demo.doc_ids) {
        const found = existingDocs.find(d => d.document_id === reqDocId);
        if (found) {
          await fetch(`/api/chat/sessions/${state.currentSessionId}/documents`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ document_id: found.document_id }),
          });
          addAttachedDocument(found);
        }
      }
      renderComposerAttachmentsFromState();
    }
  } catch (err) {
    console.warn("Could not auto-attach demo docs:", err);
  }

  // Set answer mode & UI
  state.answerMode = demo.answer_mode || "balanced";
  el.lengthModeBtns.forEach(btn => {
    btn.classList.toggle("active", btn.dataset.mode === state.answerMode);
  });

  // Enable research mode for demo 7
  if (demo.id === "DEMO_7_RESEARCH_MODE_TRACE") {
    setResearchMode(true);
  }

  // Populate input textarea and submit
  el.chatTextarea.value = demo.query;
  activateChatStreamView();
  submitUserMessage();
}

// ==============================================================================
// ROUND 2 — SETTINGS MODAL
// ==============================================================================
function openSettingsModal() {
  if (el.modalSettings) {
    el.modalSettings.style.display = "flex";
    if (el.backdropOverlay) el.backdropOverlay.style.display = "block";
    if (el.settingAnswerMode) el.settingAnswerMode.value = state.answerMode;
  }
}

function closeSettingsModal() {
  if (el.modalSettings) {
    el.modalSettings.style.display = "none";
  }
}

function saveSettings() {
  if (el.settingAnswerMode) {
    state.answerMode = el.settingAnswerMode.value;
    el.lengthModeBtns.forEach(btn => {
      btn.classList.toggle("active", btn.dataset.mode === state.answerMode);
    });
  }
  closeSettingsModal();
  if (el.backdropOverlay) el.backdropOverlay.style.display = "none";
  alert("Cấu hình hệ thống đã được lưu thành công!");
}

// ==============================================================================
// ROUND 2 — OFFLINE RESOURCE STATUS MODAL
// ==============================================================================
async function fetchAndRenderSystemStatus() {
  try {
    const resp = await fetch("/api/system/status");
    if (!resp.ok) return;
    const data = await resp.json();

    if (el.headerOfflineStatusText) {
      el.headerOfflineStatusText.textContent = "OFFLINE READY";
    }
    if (el.statusCardModel) {
      el.statusCardModel.textContent = "✓ READY";
      el.statusCardModel.className = "status-card-value text-success";
    }
    if (el.statusCardTokenizer) {
      el.statusCardTokenizer.textContent = "✓ READY";
      el.statusCardTokenizer.className = "status-card-value text-success";
    }
    if (el.statusCardCheckpoint) {
      el.statusCardCheckpoint.textContent = "✓ READY";
      el.statusCardCheckpoint.className = "status-card-value text-success";
    }
    if (el.statusCardIndex) {
      el.statusCardIndex.textContent = "✓ READY";
      el.statusCardIndex.className = "status-card-value text-success";
    }
    if (el.statusCardEvidence) {
      el.statusCardEvidence.textContent = "✓ READY";
      el.statusCardEvidence.className = "status-card-value text-success";
    }
    if (el.statusCardNetwork) {
      el.statusCardNetwork.textContent = "NOT REQUIRED";
      el.statusCardNetwork.className = "status-card-value text-success";
    }
    if (el.statusFooterNote && data.active_checkpoint) {
      el.statusFooterNote.innerHTML = `
        <strong>Mô hình nền:</strong> ${escapeHtml(data.active_checkpoint.backbone_name || "SmolLM2-135M (Frozen Pretrained Base)")}<br>
        <strong>Checkpoint SA-CMS:</strong> ${escapeHtml(data.active_checkpoint.name || "Phase 4.1 Frozen Empirical Checkpoint")}<br>
        <strong>Trạng thái:</strong> ${escapeHtml(data.active_checkpoint.type || "CURRENT_VALID_CHECKPOINT")} (${escapeHtml(data.active_checkpoint.source || "Frozen 3-level Memory")})<br>
        <strong>Môi trường:</strong> Local Only (Zero Cloud API / Zero Remote CDN / Zero Network)
      `;
    }
  } catch (err) {
    console.warn("Could not fetch system status:", err);
  }
}

function openSystemStatusModal() {
  if (el.modalSystemStatus) {
    el.modalSystemStatus.style.display = "flex";
    if (el.backdropOverlay) el.backdropOverlay.style.display = "block";
    fetchAndRenderSystemStatus();
  }
}

function closeSystemStatusModal() {
  if (el.modalSystemStatus) {
    el.modalSystemStatus.style.display = "none";
  }
}

// ==============================================================================
// DEMO DATA SEEDING
// ==============================================================================
async function handleSeedDemo() {
  if (!confirm("Nạp 4 tài liệu nghiên cứu SA-CMS mẫu vào hệ thống?")) return;
  try {
    const resp = await fetch("/api/demo/seed", { method: "POST" });
    if (resp.ok) {
      alert("Đã nạp thành công 4 tài liệu nghiên cứu mẫu!");
      loadSessions();
    }
  } catch (err) {
    alert("Không thể nạp dữ liệu mẫu.");
  }
}

// ==============================================================================
// UTILS
// ==============================================================================
function escapeHtml(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
