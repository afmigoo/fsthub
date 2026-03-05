const error_dialog = document.getElementById("error-dialog");
const error_dialog_msg = document.getElementById("error-dialog-msg");
const error_dialog_title = document.getElementById("error-dialog-title");
const error_dialog_close = document.getElementById("error-dialog-close");

/** Error display */
function show_error(message) {
    error_dialog_msg.textContent = message;
    if (!error_dialog.open)
        error_dialog.showModal();
}
function hide_error() {
    error_dialog.close();
}
error_dialog_close.addEventListener("click", () => {
    hide_error();
});

/** API logic */
class TooManyRequests extends Error {
  constructor(message) {
    super(message);
    this.name = "TooManyRequests";
  }
}
class NotFound extends Error {
  constructor(message) {
    super(message);
    this.name = "NotFound";
  }
}
class BadRequest extends Error {
  constructor(message) {
    super(message);
    this.name = "BadRequest";
  }
}

function form_href(url, params = {}) {
    // Create the URL with parameters
    const url_obj = new URL(url);    
    Object.entries(params).forEach(([key, value]) => {
        url_obj.searchParams.append(key, value);
    });
    return url_obj.href;
}

function get_error_message(error) {
    if (error.name in translations['exceptions'])
        if (error.message)
            return `${translations['exceptions'][error.name]}: ${error.message}`;
        else
            return translations['exceptions'][error.name];
    return error.message || "Unexpected error occurred.";
}

async function call_api(url, params = {}, options = {}, method = 'GET') {
    try {
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
        if (response.status == 400)
            throw new BadRequest(await response.text());
        // if (response.status == 404)
        //     throw new NotFound();
        if (response.status == 429)
            throw new TooManyRequests();
        if (!response.ok)
            throw new Error(`API returned ${response.status}(${response.statusText})\n${await response.text()}`);
        // Check content type
        const contentType = response.headers.get('content-type');
        const isJson = contentType && contentType.includes('application/json');
        // Return the result
        if (isJson)
            return await response.json()    
        throw new Error(`API returned invalid format: ${response}`);
    } catch (exception) {
        console.error("API call failed", {
            method: method,
            url: url,
            params: params,
            options: options
        });
        throw exception;
    }
}

/** Globals */
function remove_children(element) {
    element.innerHTML = '';
}