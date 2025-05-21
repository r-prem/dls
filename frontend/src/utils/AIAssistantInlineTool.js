export default class AIAssistantInlineTool {
  static get isInline() {
    return true;
  }

  static get title() {
    return 'AI Assistant';
  }

  static get sanitize() {
    return {
      ai: true,
    };
  }

  constructor({ api }) {
    this.api = api;
    this.button = null;
    this.selectedText = '';
  }

  render() {
    this.button = document.createElement('button');
    this.button.type = 'button';
    this.button.innerHTML = '🤖';
    this.button.title = 'AI Assistant';
    return this.button;
  }

  surround(range) {
    this.selectedText = range.toString();
    this.button.disabled = true;
    this.button.innerHTML = '<svg class="animate-spin" width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" stroke="#888" stroke-width="2" fill="none" stroke-dasharray="22" stroke-dashoffset="10"></circle></svg>';

    let headers = {};
    const token = window.csrf_token;
    if(window.origin.includes('localhost')) {
      headers = { 'Content-Type': 'application/json' };
    } else {
      headers = { 'Content-Type': 'application/json', 'X-frappe-csrf-token': token, 'X-frappe-site-name': window.origin };
    }

    fetch('/api/method/dls.dls.api.openai_generate_response', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({ prompt: this.selectedText }),
    })
      .then(res => res.json())
      .then(data => {
        const aiText = data.message?.choices?.[0]?.message?.content || '';
        this.showPreviewModal(this.selectedText, aiText, () => {
          range.deleteContents();
          range.insertNode(document.createTextNode(aiText));
        });

      })
      .catch((e) => {
        console.log(e);
        alert('AI generation failed');
      })
      .finally(() => {
        this.button.disabled = false;
        this.button.innerHTML = '🤖';
      });
  }

  showPreviewModal(original, suggestion, onAccept) {
    // Remove any existing modal
    const existing = document.getElementById('ai-preview-modal');
    if (existing) existing.remove();
  
    // Modal overlay
    const overlay = document.createElement('div');
    overlay.id = 'ai-preview-modal';
    overlay.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40';
    overlay.tabIndex = -1;
  
    // Modal box
    const box = document.createElement('div');
    box.className = 'bg-white rounded-lg shadow-xl max-w-lg w-full p-6';
  
    // Modal header
    const header = document.createElement('div');
    header.className = 'mb-4';
    const title = document.createElement('h3');
    title.className = 'text-lg font-semibold';
    title.innerHTML = window.__ ? window.__('AI Suggestion Preview') : 'AI Suggestion Preview';
    header.appendChild(title);
  
    // Modal body
    const body = document.createElement('div');
    body.className = 'mb-6';
    body.innerHTML = `
      <div class="mb-2 font-medium">${window.__ ? window.__('Original') : 'Original'}:</div>
      <div class="bg-gray-100 p-2 rounded mb-4 whitespace-pre-wrap">${original}</div>
      <div class="mb-2 font-medium">${window.__ ? window.__('Suggestion') : 'Suggestion'}:</div>
      <div class="bg-blue-50 p-2 rounded whitespace-pre-wrap">${suggestion}</div>
    `;
  
    // Modal footer
    const footer = document.createElement('div');
    footer.className = 'flex justify-end gap-2';
  
    const acceptBtn = document.createElement('button');
    acceptBtn.className = 'mt-3 md:mt-0 inline-flex items-center justify-center gap-2 transition-colors focus:outline-none text-ink-white bg-surface-gray-7 hover:bg-surface-gray-6 active:bg-surface-gray-5 focus-visible:ring focus-visible:ring-outline-gray-3 h-7 text-base px-2 rounded';
    acceptBtn.innerHTML = window.__ ? window.__('Accept') : 'Accept';
    acceptBtn.onclick = () => {
      onAccept();
      overlay.remove();
    };
  
    const declineBtn = document.createElement('button');
    declineBtn.className = 'mt-3 md:mt-0 inline-flex items-center justify-center gap-2 transition-colors focus:outline-none hover:bg-surface-gray-6 active:bg-surface-gray-5 focus-visible:ring focus-visible:ring-outline-gray-3 h-7 text-base px-2 rounded';
    declineBtn.style.background = 'transparent';
    declineBtn.style.border = 'none';
    declineBtn.innerHTML = window.__ ? window.__('Decline') : 'Decline';
    declineBtn.onclick = () => {
      overlay.remove();
    };
  
    footer.appendChild(declineBtn);
    footer.appendChild(acceptBtn);
  
    // Assemble modal
    box.appendChild(header);
    box.appendChild(body);
    box.appendChild(footer);
    overlay.appendChild(box);
    document.body.appendChild(overlay);
  
    // Close modal on overlay click (optional)
    overlay.onclick = (e) => {
      if (e.target === overlay) overlay.remove();
    };
  }


  checkState() {
    // Optional: highlight button if selection is active
  }
} 