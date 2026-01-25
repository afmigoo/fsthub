const title = document.getElementById("title");
const meta_container = document.getElementById("meta-container");
const example_container = document.getElementById("example-container");
const interact_button = document.getElementById("interact");

/** Metadata fetching logic */
function display_metadata(data) {
    remove_children(meta_container);
    for (const key in data) {
        if (data[key] == null | data[key] == "")
            continue;
        const li = document.createElement('li');
        li.innerHTML = `<b>${key}</b>: ${data[key]}`
        meta_container.appendChild(li);
    }
}
async function load_meta() {
    await call_api(api_metadata_url, {
        'hfst_file': selected_transducer
    })
    .then((data) => {
        console.log(data);
        title.innerHTML = selected_transducer;
        display_metadata(data['metadata']);
    })
    .catch((error) => {
        if (error instanceof NotFound)
            title.innerText = selected_project;
        else 
            throw error;
    })
}
/** Example fetching logic */
function display_example(data) {
    remove_children(example_container);
    for (const key of ['input', 'output']) {
        const li = document.createElement('li');
        const label = document.createElement('b');
        label.textContent = translate[key];
        console.log(label, data[key])
        li.append(label, ': ', data[key]);
        example_container.appendChild(li);
    }
}
async function load_example() {
    await call_api(api_example_url, {
        'hfst_file': selected_transducer
    })
    .then((data) => {
        console.log(data);
        title.innerHTML = selected_transducer;
        display_example(data['example']);
    })
    .catch((error) => {
        if (error instanceof NotFound)
            title.innerText = selected_project;
        else 
            throw error;
    })
}

/** Events */
async function on_load() {
    await load_meta();
    await load_example();
}
document.addEventListener('DOMContentLoaded', async () => {
    await on_load()
});