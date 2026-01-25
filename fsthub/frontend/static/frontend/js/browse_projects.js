const input_textbox = document.getElementById("input-textbox");
const input_button = document.getElementById("input-button");
const results_list = document.getElementById("results-list");
const results_footer = document.getElementById("results-footer");

/* Search logic */
function add_result_item(project) {
    const article = document.createElement('article');
    const link = document.createElement('a');
    link.innerText = `${project['name']}`;
    link.href = project_base_url + project['name'];
    article.classList.add('result-item');
    article.appendChild(link);
    results_list.appendChild(article);
}
function set_page_buttons(prev_href, next_href) {
    const prev = document.createElement('button');
    const next = document.createElement('button');
    //const page = document.createElement('span');
    prev.innerText = '<';
    if (prev_href == null) 
        prev.disabled = true;
    else 
        prev.addEventListener("click", async () => update_results(prev_href));
    next.innerText = '>'; 
    if (next_href == null) 
        next.disabled = true;
    else 
        next.addEventListener("click", async () => update_results(next_href));
    //page.innerText = `${page_num}`;
    results_footer.appendChild(prev);
    //results_footer.appendChild(page);
    results_footer.appendChild(next);
}
function clear_results() {
    remove_children(results_list);
    remove_children(results_footer);
}
function display_results(data) {
    projects = data['results'];
    for (p in projects)
        add_result_item(projects[p]);
    set_page_buttons(data['previous'], data['next']);
}
async function update_results(href) {
    clear_results();
    await call_api(href)
        .then((data) => display_results(data))
        .catch((error) => {
            display_error(results_list, error);
            throw error;
        })
}

/* Events */
input_button.addEventListener("click", async () => {
    await update_results(api_search_url);
});
document.addEventListener('DOMContentLoaded', async () => {
    await update_results(api_search_url);
});