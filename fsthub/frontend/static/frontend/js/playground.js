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
const fst_format_select = document.getElementById("fst-format");
const file_export_button = document.getElementById("file-export-button");


function create_option(text, selected=false) {
    const op = document.createElement('option');
    op.value = text;
    op.innerText = text;
    op.selected = selected;
    return op;
}
function populate_select(select_obj, options, flush_children=false) {
    if (flush_children)
        remove_children(select_obj);
    for (i in options)
        select_obj.appendChild(create_option(options[i]));
}

/** Filters logic */
function display_filters(select_obj, filters) {
    const filter_names = filters.map(x => x.name);
    remove_children(select_obj);
    select_obj.appendChild(create_option('all', selected=true));
    populate_select(select_obj, filter_names, flush_children=false)
}
async function init_filters() {
    console.debug('init_filters start');
    const types = await call_api(api_fetch_types_url);
    const langs = await call_api(api_fetch_langs_url);
    display_filters(fst_type_select, types);
    display_filters(fst_lang_select, langs);
    console.debug('init_filters end');
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
    const data = await call_api(api_example_url, {
        'hfst_file': transducer_name
    })
    console.info("Loaded example", data);
    display_example(data['example']);
}
/** Fst output formats logic */
async function init_fst_out_formats() {
    console.debug('init_fst_out_formats start');
    const data = await call_api(api_fetch_fst_out_formats);
    populate_select(fst_format_select, data['formats'], flush_children=true);
    console.debug('init_fst_out_formats end');
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
    console.debug('update_results start');
    const params = get_filter_params();
    const data = await call_api(api_fetch_fst_url, params)
    display_fsts(data['results']);
    console.debug('update_results end');
    await load_example(fst_name_select.value);
}
/** Transducer calling logic */
async function call_fst() {
    fst_box['output'].value = "";
    try {
        data = await call_api(api_call_fst_url, {}, {
            body: JSON.stringify({
                "fst_input": fst_box['input'].value,
                "hfst_file": fst_name_select.value,
                "output_format": fst_format_select.value
            }),
            method: 'POST'
        })
    } catch (exception) {
        show_error(
            `${translations['plain']['error_failed_to_call_fst']}: ${get_error_message(exception)}`
        );
        throw exception;
    };
    fst_box['output'].value = data["output"];
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
async function on_filter_change() {
    hide_error(error_dialog, error_dialog_msg);
    await update_results();
}
async function on_load() {
    await init_filters()
        .catch((exception) => {
            show_error(
                `${translations['plain']['error_failed_to_fetch_filters']}: ${get_error_message(exception)}`
            );
            throw exception;
        });
    await on_filter_change()
        .catch((exception) => {
            show_error(
                `${translations['plain']['error_failed_to_update_transducers']}: ${get_error_message(exception)}`
            );
            throw exception;
        });
    
    var fsts = fst_name_select.children;
    for (var i = 0; i < fsts.length; i++) {
        if (fsts[i].value == selected_fst)
            fsts[i].selected = true;
    }

    await load_example(fst_name_select.value)
        .catch((exception) => {
            show_error(
                `${translations['plain']['error_failed_to_load_example']}: ${get_error_message(exception)}`
            );
            throw exception;
        });

    await init_fst_out_formats()
        .catch((exception) => {
            show_error(
                `${translations['plain']['error_failed_to_fetch_fst_out_formats']}: ${get_error_message(exception)}`
            );
            throw exception;
        });
}
send_button.addEventListener("click", async () => {
    hide_error(error_dialog, error_dialog_msg);
    await call_fst();
});
fst_name_select.addEventListener("change", async () => {
    await load_example(fst_name_select.value);
});
fst_example_str['input'].addEventListener("click", () => {
    fst_box['input'].value = fst_example_str['input'].innerText;
});
fst_type_select.addEventListener("change", async () => {
    await on_filter_change();
});
fst_lang_select.addEventListener("change", async () => {
    await on_filter_change();
});
file_export_button.addEventListener('click', file_export);
document.addEventListener('DOMContentLoaded', async () => {
    on_load()
});
