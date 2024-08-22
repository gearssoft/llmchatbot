
export default async function main() {
    const input = document.getElementById('input');
    const send = document.getElementById('send');
    const output = document.getElementById('output');

    send.addEventListener('click', async function () {
        const text = input.value;
        input.value = '';
        output.innerHTML += '<div>' + text + '</div>';

        try {
            const response = await fetch('http://gears001.iptime.org:22290/jb14/qa_stream', {
                method: 'POST',
                headers: {
                    'Content-Type': 'text/plain'
                },
                body: text
            });

            const reader = response.body.getReader();
            let receivedLength = 0; // 받은 길이
            let chunks = []; // 받은 바이너리 청크를 모으는 배열
            while (true) {
                const { done, value } = await reader.read();

                console.log(done, value);

                if (done) {
                    break;
                }

                chunks.push(value);
                receivedLength += value.length;
                // 바이너리 청크를 텍스트로 변환
                let textChunk = new TextDecoder("utf-8").decode(value, { stream: true });
                output.innerHTML += textChunk;
            }

            // 모든 청크를 하나의 Uint8Array로 결합
            let chunksAll = new Uint8Array(receivedLength);
            let position = 0;
            for (let chunk of chunks) {
                chunksAll.set(chunk, position);
                position += chunk.length;
            }

            // 텍스트로 디코드
            let result = new TextDecoder("utf-8").decode(chunksAll);
            console.log(result);
            //output.innerHTML += '<div>' + result + '</div>';

        } catch (err) {
            console.error('Fetch error', err);
        }
    });
}