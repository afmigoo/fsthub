const input_textbox = document.getElementById("input-textbox");
const input_button = document.getElementById("input-button");
const results_list = document.getElementById("results-list");
const results_footer = document.getElementById("results-footer");

/* Globals */
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

/* Search logic */
function add_result_item(project) {
    const div = document.createElement('div');
    const link = document.createElement('a');
    link.innerText = `${project['directory']}`;
    link.href = project_base_url + project['id'];
    div.classList.add('result-item');
    div.appendChild(link);
    results_list.appendChild(div);
}
function set_page_buttons(prev_href, next_href) {
    const prev = document.createElement('button');
    const next = document.createElement('button');
    //const page = document.createElement('span');
    prev.innerText = '<';
    if (prev_href == null) 
        prev.disabled = true;
    else 
        prev.addEventListener("click", async () => display_api_result(prev_href));
    next.innerText = '>'; 
    if (next_href == null) 
        next.disabled = true;
    else 
        next.addEventListener("click", async () => display_api_result(next_href));
    //page.innerText = `${page_num}`;
    results_footer.appendChild(prev);
    //results_footer.appendChild(page);
    results_footer.appendChild(next);
}
async function display_api_result(href) {
    remove_children(results_list);
    remove_children(results_footer);
    await call_api(href)
        .catch((error) => {
            display_error(results_list, error);
            throw error;
        })
        .then((data) => {
            projects = data['results'];
            for (p in projects)
                add_result_item(projects[p]);
            set_page_buttons(data['previous'], data['next']);
        })
}

/* Events */
input_button.addEventListener("click", async () => {
    await display_api_result(api_search_url);
});
document.addEventListener('DOMContentLoaded', async () => {
    await display_api_result(api_search_url);
});