function init() {
    const compilers = ["clang"];

    async function update(compiler) {
        const result = await fetch(`https://lambda.compiler-explorer.com/compiler-build/${compiler}`);
        return [compiler, await result.json()];
    }

    async function updateAll() {
        const results = await Promise.all(compilers.map(c => update(c)));
        results.sort();
        console.log(results);
    }
    updateAll();
}

init();
