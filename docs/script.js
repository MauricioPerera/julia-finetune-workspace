const button = document.querySelector('#copy-prompt');
button?.addEventListener('click', async () => {
  const text = document.querySelector('#agent-prompt').textContent.trim();
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = 'Mensaje copiado. Pégalo en tu IA con acceso a archivos y terminal.';
    button.textContent = 'Copiado ✓';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#agent-prompt'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Seleccionamos el mensaje. Usa Ctrl+C o la opción Copiar de tu dispositivo.';
  }
});
