function form_href(url, params = {}) {
    // Create the URL with parameters
    const url_obj = new URL(url);    
    Object.entries(params).forEach(([key, value]) => {
        url_obj.searchParams.append(key, value);
    });
    return url_obj.href;
}

async function call_api(url, params = {}, options = {}) {
    const href = form_href(url, params);
    // Merge default options with provided ones
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    };
    const mergedOptions = { ...defaultOptions, ...options };
    const response = await fetch(href, mergedOptions);

    if (!response.ok) {
        throw new Error(`API returned ${response.status}(${response.statusText})\n${await response.text()}`);
    }

    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');

    return isJson ? await response.json() : await response.text();
}