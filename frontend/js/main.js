function parseWords(data) {
  for(let i = 0; i < data.length; i++) {
    data[i].text = data[i].word;
    data[i].weight = data[i].count;
    delete data[i].word;
    delete data[i].count;
  }
}

function showHeadline(url) {
  $('.js-clouds-head').addClass('active');
  $('.js-clouds-head').append(url);
}

function renderCloud(data) {
  $('#cloud-results').show();
  parseWords(data);
  $('#cloud-results').jQCloud(data);
}

function crawlSite(url) {
  $.ajax({
    method: 'GET',
    url: 'crawl',
    data: {url: url},
    success: function(result){
      renderCloud(result);
    }
  });
}

function validate(url) {
  var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
  var regex = new RegExp(expression);
  
  if(url.match(regex)) {
    return true;
  }
  return false
}

function showError() {
  $('.form__group').addClass("error");
  $('.form__msg').show();
}

$(function() {
  $('#cloud-results').hide();
  let btn = $('#submit');
  let form = $('.js-form');
  btn.click(function() {
    if(validate($('input[type=text]').val())) {
      let url = $('input[type=text]').val();
      form.hide();
      crawlSite(url);
      showHeadline(url);
    } else {
      showError();
    }
  })
});