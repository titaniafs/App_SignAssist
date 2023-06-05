class Chatbox {
    constructor() {
      this.args = {
        openButton: document.querySelector('.chatbox__button'),
        chatBox: document.querySelector('.chatbox__support'),
        sendButton: document.querySelector('.send__button'),
        inputField: document.querySelector('.chatbox__footer input'),
        chatMessages: document.querySelector('.chatbox__messages')
      };
  
      this.state = false;
      this.messages = [];
    }
  
    display() {
      const { openButton, chatBox, sendButton, inputField } = this.args;
  
      openButton.addEventListener('click', () => this.toggleState(chatBox));
  
      sendButton.addEventListener('click', () => this.onSendButton(chatBox));
  
      inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
          this.onSendButton(chatBox);
        }
      });
    }
  
    toggleState(chatbox) {
      this.state = !this.state;
  
      if (this.state) {
        chatbox.classList.add('chatbox--active');
      } else {
        chatbox.classList.remove('chatbox--active');
      }
    }
  
    onSendButton(chatbox) {
      const inputField = this.args.inputField;
      const message = inputField.value.trim();
  
      if (message === '') {
        return;
      }
  
      const userMsg = { name: 'User', message };
      this.messages.push(userMsg);
      this.updateChatText(chatbox);
  
      const params = new URLSearchParams({ msg: message });
      fetch('/get?' + params, { method: 'GET' })
        .then((response) => response.text())
        .then((data) => {
          const botMsg = { name: 'Sam', message: data };
          this.messages.push(botMsg);
          this.updateChatText(chatbox);
        })
        .catch((error) => {
          console.error('Error:', error);
        });
  
      inputField.value = '';
    }
  
    updateChatText(chatbox) {
      const chatMessages = this.args.chatMessages;
      let html = '';
  
      this.messages.slice().reverse().forEach((item) => {
        const className = item.name === 'Sam' ? 'messages__item--visitor' : 'messages__item--operator';
        html += `<div class="messages__item ${className}">${item.message}</div>`;
      });
  
      chatMessages.innerHTML = html;
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }
  
  const chatbox = new Chatbox();
  chatbox.display();
  
  function getBotResponse() {
    const inputField = document.getElementById('textInput');
    const userText = inputField.value.trim();
  
    if (userText === '') {
      return;
    }
  
    const userHtml = `<p class="userText" style="color: white;"><span>${userText}</span></p>`;
    const chatbox = document.querySelector('.chatbox__support');
    chatbox.querySelector('.chatbox__messages').insertAdjacentHTML('beforeend', userHtml);
    chatbox.classList.add('chatbox--active');
  }  