async function loadFile(url) {
    try {
        const response = await fetch(url);
        const data = await response.text();
        console.log(data);
    } catch (err) {
        console.error(err);
    }
}

loadFile("data/item-data.csv");