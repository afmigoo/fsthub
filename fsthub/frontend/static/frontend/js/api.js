/** API logic */
function form_href(url, params = {}) {
    // Create the URL with parameters
    const url_obj = new URL(url);    
    Object.entries(params).forEach(([key, value]) => {
        url_obj.searchParams.append(key, value);
    });
    return url_obj.href;
}

class TooManyRequests extends Error {
  constructor(message) {
    super(message); // (1)
    this.name = "TooManyRequests"; // (2)
  }
}

class NotFound extends Error {
  constructor(message) {
    super(message); // (1)
    this.name = "NotFound"; // (2)
  }
}

async function call_api(url, params = {}, options = {}, method = 'GET') {
    const href = form_href(url, params);
    // Merge default options with provided ones
    const defaultOptions = {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    const mergedOptions = { ...defaultOptions, ...options };
    // Execute request
    const response = await fetch(href, mergedOptions);
    if (response.status == 429)
        throw new TooManyRequests();
    if (response.status == 404)
        throw new NotFound();
    if (!response.ok)
        throw new Error(`API returned ${response.status}(${response.statusText})\n${await response.text()}`);
    // Check content type
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');
    // Return the result
    if (isJson)
        return await response.json()    
    throw new Error(`API returned invalid format: ${response}`);
}

/** Globals */
function remove_children(element) {
    element.innerHTML = '';
}
function display_error(element, message) {
    remove_children(element);
    const text = document.createElement('p');
    text.innerText = message;
    text.style.color = 'red';
    element.appendChild(text);
}