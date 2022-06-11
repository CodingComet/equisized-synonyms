function redirect(words) {
    let disable_spaces =
        document.getElementById("disable_spaces").checked;
    let hide_partial_rows =
        document.getElementById("hide_partial_rows").checked;

    window.location.href = `/get/${words}?disable_spaces=${disable_spaces}&hide_partial_rows=${hide_partial_rows}`;
}

function refresh() {
    let word_elements = document.getElementsByName("word");
    let words = [];
    word_elements.forEach(word_element => {
        words.push(word_element.innerText);
    });

    redirect(words);
}