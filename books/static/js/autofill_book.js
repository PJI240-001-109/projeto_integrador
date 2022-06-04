is_isbn = (str) => {
  var sum, weight, digit, check, i;

  str = str.replace(/[^0-9X]/gi, "");

  if (str.length != 10 && str.length != 13) {
    return false;
  }

  if (str.length == 13) {
    sum = 0;
    for (i = 0; i < 12; i++) {
      digit = parseInt(str[i]);
      if (i % 2 == 1) {
        sum += 3 * digit;
      } else {
        sum += digit;
      }
    }
    check = (10 - (sum % 10)) % 10;
    return check == str[str.length - 1];
  }

  if (str.length == 10) {
    weight = 10;
    sum = 0;
    for (i = 0; i < 9; i++) {
      digit = parseInt(str[i]);
      sum += weight * digit;
      weight--;
    }
    check = (11 - (sum % 11)) % 11;
    if (check == 10) {
      check = "X";
    }
    return check == str[str.length - 1].toUpperCase();
  }
};

normalize_isbn = (raw_isbn) => {
  return raw_isbn.replace(/[^0-9X]/gi, "");
};

fill_book_field = (field_id, value) => {
  document.getElementById(field_id).value = value;
};

fill_book_authors = (authors) => {
  var $crf_token = django.jQuery('[name="csrfmiddlewaretoken"]').attr('value');

  // Fetch the preselected item, and add to the control
  const authorsSelect = django.jQuery('#id_authors');
  authorsSelect.val(null).trigger('change');

  authors.forEach((author) => {
    django.jQuery.ajax({

      method: 'POST',
      url: '/api/authors/get_or_create',
      data: { name: `${author}` },
      headers: { "X-CSRFToken": $crf_token },

    }).done(function (data) {

      // create the option and append to Select2
      var option = new Option(data.name, data.id, true, true);
      authorsSelect.append(option).trigger('change');

      // manually trigger the `select2:select` event
      authorsSelect.trigger({
        type: 'select2:select',
        params: {
          data: data
        }
      });
    });
  });
};

fill_book_pubsher = (publisher) => {
  var $crf_token = django.jQuery('[name="csrfmiddlewaretoken"]').attr('value');

  // Fetch the preselected item, and add to the control
  const publisherSelect = django.jQuery('#id_publisher');
  publisherSelect.val(null).trigger('change');

  django.jQuery.ajax({

    method: 'POST',
    url: '/api/publishers/get_or_create',
    data: { name: `${publisher}` },
    headers: { "X-CSRFToken": $crf_token },

  }).done(function (data) {

    // create the option and append to Select2
    var option = new Option(data.name, data.id, true, true);
    publisherSelect.append(option).trigger('change');

    // manually trigger the `select2:select` event
    publisherSelect.trigger({
      type: 'select2:select',
      params: {
        data: data
      }
    });
  });
};

fill_book = (json) => {

  if (json.items) {
    const book = json.items[0];

    // Title
    fill_book_field("id_title", book.volumeInfo.title);

    // Authors
    fill_book_authors(book.volumeInfo.authors);

    // Publisher
    fill_book_pubsher(book.volumeInfo.publisher);

    // Year
    const year = new Date(book.volumeInfo.publishedDate).getFullYear();
    fill_book_field("id_year", year);

    // Page count
    fill_book_field("id_page_count", book.volumeInfo.pageCount);
  }
};

try_fill_book = () => {
  const input = document.getElementById("id_isbn");

  if (input && is_isbn(input.value)) {
    const isbn = normalize_isbn(input.value);
    var xhr = new XMLHttpRequest();
    xhr.open(
      "GET",
      `https://www.googleapis.com/books/v1/volumes?q=isbn%3D${isbn}&maxResults=1`,
      true
    );

    xhr.onreadystatechange = function () {
      if (xhr.readyState != 4 || xhr.status != 200) {
        return;
      }
      fill_book(JSON.parse(xhr.response));
    };
    xhr.send(null);
  }
};
