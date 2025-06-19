const fst_name_select = document.getElementById("fst-name");
const fst_type_select = document.getElementById("fst-type");
const fst_lang_select = document.getElementById("fst-lang");
const input_box = document.getElementById("fst-input-box");
const output_box = document.getElementById("fst-output-box");
const send_button = document.getElementById("fst-send");
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
    return await call_api(url)
        .then((data) => {
            return data['results'];
        })
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
/** Transducer list logic */
function display_fsts(transducers) {
    remove_children(fst_name_select);
    for (i in transducers) {
        const name = transducers[i]['file_path'];
        if (name == undefined) {
            throw new Error(`fst['file_path'] is undefined; ${JSON.stringify(transducers)}`)
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
            display_fsts(data);
        });
    console.log('update_results end');
}
/** Transducer calling logic */
async function call_fst() {
    ratelimit_box.hidden = true;
    output_box.value = "";
    await call_api(api_call_fst_url, {}, {
        body: JSON.stringify({
            "fst_input": input_box.value,
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
        output_box.value = data["output"];
    })
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
}
document.addEventListener('DOMContentLoaded', async () => {
    on_load()
});