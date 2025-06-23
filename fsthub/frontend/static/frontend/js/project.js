const title = document.getElementById("title");
const meta_container = document.getElementById("meta-container");
const fst_container = document.getElementById("fst-container");
const fst_empty_text = document.getElementById("fst-empty-text");

/** Metadata fetching logic */
function display_metadata(data) {
    for (const key in data) {
        if (data[key] == null | data[key] == "")
            continue;
        const li = document.createElement('li');
        li.innerHTML = `<b>${key}:</b> ${data[key]}`
        meta_container.appendChild(li);
    }
}
async function load_meta() {
    await call_api(api_metadata_url + selected_project)
    .then((data) => {
        console.log(data);
        title.innerHTML = data["directory"];
        delete data['directory'];
        display_metadata(data);
    })
    .catch((error) => {
        if (error instanceof NotFound)
            title.innerText = selected_project;
        else 
            throw error;
    })
}

/** Transducer fetching logic */
function display_fsts(data) {
    if (data.length == 0) 
        fst_empty_text.hidden = false;
    for (const it in data) {
        console.log(it);
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.href = fst_url + data[it]['name'];
        a.innerText = data[it]['name'];
        li.appendChild(a);
        fst_container.appendChild(li);
    }
}
async function load_fst_list() {
    await call_api(api_fst_list_url, {
        'project': selected_project
    })
    .then((data) => {
        display_fsts(data['results']);
    })
}

/** Events */
async function on_load() {
    await Promise.all([
        load_meta(),
        load_fst_list()
    ]);
}
document.addEventListener('DOMContentLoaded', async () => {
    await on_load()
});