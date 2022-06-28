let value;
chrome.runtime.onMessage.addListener((message, sender, sendResponse) =>{
  switch (message.method){
  case 'Send':
    value = message.value;
    break;
  case 'Recv':
    sendResponse({value: value});
    break;
  }
});