
document.getElementById('igbot').onclick = () => {
  chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
    chrome.scripting.executeScript({
      target: {tabId: tabs[0].id},
      function: RecvFromDomainA
    });
  });
}

function RecvFromDomainA(){
  var url = window.location.pathname
  var url2 = ("https://alpine-freedom-346707.uc.r.appspot.com" + url)
  alert('We will go to  ' + url2);
  alert("success1");

  var opts = {
    method: 'GET',      
    headers: {}
  };
  fetch(url2, opts).then(function (response) {
    return response.text();
  })
  .then(function (text) {
    alert(text);
    document.querySelector('.QGPIr').innerHTML = text
  });

}
