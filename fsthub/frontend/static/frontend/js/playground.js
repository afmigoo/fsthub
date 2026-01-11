const fst_name_select = document.getElementById("fst-name");
const fst_type_select = document.getElementById("fst-type");
const fst_lang_select = document.getElementById("fst-lang");
const fst_example_box = {
    "input": document.getElementById("fst-example-input-box"),
    "output": document.getElementById("fst-example-output-box")
};
const fst_example_str = {
    "input": document.getElementById("fst-example-input-str"),
    "output": document.getElementById("fst-example-output-str")
};
const fst_box = {
    "input": document.getElementById("fst-input-box"),
    "output": document.getElementById("fst-output-box")
};
const send_button = document.getElementById("fst-send");
const file_export_button = document.getElementById("file-export-button");
const error_box = document.getElementById("error-box");
const ratelimit_box = document.getElementById("ratelimit-box");


function create_option(text) {
    const op = document.createElement('option');
    op.value = text;
    op.innerText = text;
    return op;
}

/** Filters logic */
async function get_filters(url) {
    return await call_api(url);
}
function display_filters(element, filters) {
    remove_children(element);
    all_option = create_option('all');
    all_option.selected = 'selected';
    element.appendChild(all_option);
    for (i in filters) {
        const name = filters[i]['name'];
        if (name == undefined) {
            throw new Error(`Filter['name'] is undefined; ${JSON.stringify(filters)}`)
        }
        element.appendChild(create_option(name));
    }
}
async function init_filters() {
    console.log('Init_filters start');
    const types = await get_filters(api_fetch_types_url);
    const langs = await get_filters(api_fetch_langs_url);
    display_filters(fst_type_select, types);
    display_filters(fst_lang_select, langs);
    console.log('Init_filters end');
}
/** Example fetching logic */
function display_example(data) {
    // this variand loads input AND output examples
    // i find it excessive
    // for (const key in fst_example_str) {
    //     fst_example_str[key].innerText = data[key];
    //     fst_example_box[key].hidden = false;
    // }
    fst_example_str['input'].innerText = data['input'];
    fst_example_box['input'].hidden = false;
}
async function load_example(transducer_name) {
    for (const key in fst_example_str) {
        fst_example_str[key].innerText = '';
        fst_example_box[key].hidden = true;
    }
    await call_api(api_example_url, {
        'hfst_file': transducer_name
    })
    .then((data) => {
        console.log(data);
        display_example(data['example']);
    })
}
/** Transducer list logic */
function display_fsts(transducers) {
    remove_children(fst_name_select);
    for (i in transducers) {
        const name = transducers[i]['name'];
        if (name == undefined) {
            throw new Error(`fst['name'] is undefined; ${JSON.stringify(transducers)}`)
        }
        const op = create_option(name);
        fst_name_select.appendChild(op);
    }
}
function get_filter_params() {
    // TODO VALIDATION
    const params = {};
    if (fst_type_select.value != 'all')
        params.type = fst_type_select.value;
    if (fst_lang_select.value != 'all')
        params.lang = fst_lang_select.value;
    return params;
}
async function update_results() {
    console.log('update_results start');
    const params = get_filter_params();
    await call_api(api_fetch_fst_url, params)
        .then((data) => {
            display_fsts(data['results']);
        });
    console.log('update_results end');
    await load_example(fst_name_select.value);
}
/** Transducer calling logic */
async function call_fst() {
    ratelimit_box.hidden = true;
    fst_box['output'].value = "";
    await call_api(api_call_fst_url, {}, {
        body: JSON.stringify({
            "fst_input": fst_box['input'].value,
            "hfst_file": fst_name_select.value
        }),
        method: 'POST'
    })
    .catch((error) => {
        if (error instanceof TooManyRequests) 
            ratelimit_box.hidden = false;
        else 
            throw error;
    })
    .then((data) => {
        fst_box['output'].value = data["output"];
    })
}
/** Output export logic */
function file_export() {
    if (fst_box['output'].value == '') {
        alert(translations['error_export_output_empty']);
        return;
    }
    var tmp = document.createElement('a');
    tmp.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(fst_box['output'].value));
    tmp.setAttribute('download', 'export.txt');
    tmp.style.display = 'none';
    document.body.appendChild(tmp);
    tmp.click();
    document.body.removeChild(tmp);
}

/** Events */
send_button.addEventListener("click", async () => {
    remove_children(error_box);
    await call_fst()
        .catch((error) => {
            display_error(error_box, `Failed to call API\n${error}`);
            throw error;
        });
});
async function on_filter_change() {
    remove_children(error_box);
    await update_results()
    .catch((error) => {
        display_error(error_box, `Failed to update transducers\n${error}`);
            throw error;
        })
    }
    async function on_load() {
    await init_filters()
        .catch((error) => {
            display_error(error_box, `Failed to fetch filters\n${error}`);
            throw error;
        })
        .then(async () => {
            fst_type_select.addEventListener("change", async () => {
                await on_filter_change();
            });
            fst_lang_select.addEventListener("change", async () => {
                await on_filter_change();
            });
            await on_filter_change();
        })
    
        var fsts = fst_name_select.children;
    for (var i = 0; i < fsts.length; i++) {
        if (fsts[i].value == selected_fst)
            fsts[i].selected = true;
    }

    await load_example(fst_name_select.value);
}
fst_name_select.addEventListener("change", async () => {
    await load_example(fst_name_select.value);
});
fst_example_str['input'].addEventListener("click", () => {
    fst_box['input'].value = fst_example_str['input'].innerText;
});
file_export_button.addEventListener('click', file_export);
document.addEventListener('DOMContentLoaded', async () => {
    on_load()
});
