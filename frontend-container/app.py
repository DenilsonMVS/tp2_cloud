from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def home():
    return '''
    <html>
        <head><title>Song Recommender</title></head>
        <body>
            <h1>Song Recommender</h1>
            <label for="songInput">Enter Song Name:</label>
            <input type="text" id="songInput">
            <button onclick="addSong()">Add Song</button>
            <ul id="songList"></ul>
            <button onclick="submitSongs()">Submit Songs</button>
            <div id="recommendations"></div>

            <script>
                let songs = [];

                function addSong() {
                    const songInput = document.getElementById('songInput');
                    const songName = songInput.value.trim();
                    if (songName) {
                        songs.push(songName);
                        updateSongList();
                        songInput.value = '';
                    }
                }

                function updateSongList() {
                    const songListElement = document.getElementById('songList');
                    songListElement.innerHTML = '';
                    songs.forEach((song, index) => {
                        const li = document.createElement('li');
                        li.textContent = song;
                        const removeButton = document.createElement('button');
                        removeButton.textContent = 'Remove';
                        removeButton.onclick = () => {
                            songs.splice(index, 1);
                            updateSongList();
                        };
                        li.appendChild(removeButton);
                        songListElement.appendChild(li);
                    });
                }

                function submitSongs() {
                    fetch('http://0.0.0.0:8000/api/recommend', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ songs: songs })
                    })
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('recommendations').innerText = 'Recommended Songs: ' + data.songs.join(', ');
                    });
                }
            </script>
        </body>
    </html>
    '''

if __name__ == "__main__":
    app.run(debug=True)
