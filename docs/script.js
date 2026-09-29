const button = document.querySelector('#copy-prompt');
const language = document.documentElement.lang.split('-')[0];
const messages = {
  es: {copied: 'Copiado ✓', success: 'Mensaje copiado. Pégalo en tu IA con acceso a archivos y terminal.', fallback: 'Seleccionamos el mensaje. Usa Ctrl+C o la opción Copiar de tu dispositivo.'},
  en: {copied: 'Copied ✓', success: 'Message copied. Paste it into your AI agent with file and terminal access.', fallback: 'The message is selected. Use Ctrl+C or your device’s Copy option.'},
  pt: {copied: 'Copiado ✓', success: 'Mensagem copiada. Cole-a na sua IA com acesso a arquivos e terminal.', fallback: 'Selecionamos a mensagem. Use Ctrl+C ou a opção Copiar do seu dispositivo.'}
}[language] ?? {copied: 'Copied ✓', success: 'Message copied.', fallback: 'Select and copy the message.'};
document.querySelector('.language-switch')?.addEventListener('change', event => {
  const destination = new URL(event.target.value, window.location.href);
  destination.hash = window.location.hash;
  window.location.assign(destination.href);
});
button?.addEventListener('click', async () => {
  const text = document.querySelector('#agent-prompt').textContent.trim();
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = messages.success;
    button.textContent = messages.copied;
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#agent-prompt'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = messages.fallback;
  }
});
