import {
    DynamoDBClient,
    ScanCommand,
} from "https://cdn.skypack.dev/@aws-sdk/client-dynamodb?dts";

const client = new DynamoDBClient({
    region: "us-east-1",
    credentials: {
        // NB this is the credentials of a special user "anon_web_user" which has only read-only
        // access to this DB table.
        accessKeyId: 'AKIAQYRXXUUN2RYOU7E4',
        secretAccessKey: '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',
    },
});

async function getMostRecent() {
    const { Items } = await client.send(new ScanCommand({
        TableName: 'compiler-builds',
    }));
    const results = {}
    for (const item of Items) {
        const compiler = item.compiler.S;
        const duration = item.duration.N;
        const githubRunId = item.github_run_id?.S;
        const path = item.path?.S;
        const status = item.status.S;
        const timestamp = new Date(item.timestamp.S);
        const obj = { compiler, duration, githubRunId, path, status, timestamp };
        if (!results[compiler] || results[compiler].timestamp < timestamp) {
            results[compiler] = { compiler, duration, githubRunId, path, status, timestamp };
        }
    }
    return results;
}

async function refreshUI() {
    const results = await getMostRecent();
    document.getElementById("results").innerText = JSON.stringify(results);
}

refreshUI();
