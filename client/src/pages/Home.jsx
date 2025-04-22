import './Home.css'
import { useState, useEffect } from 'react';
import axios from 'axios';

function Home() {
    const [fileUploaded, setFileUploaded] = useState(null);

    function handleDrop(event) {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file) {
            setFileUploaded(file);
        }
    }

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            setFileUploaded(file);
        }
        console.log("worked")
    }

    function handleDragOver(event) {
        event.preventDefault();
    }

    async function splitVideo(event) {
        event.preventDefault();
        if (!fileUploaded) {
            alert("Please upload a video file first.");
            return;
        }
        // if (fileUploaded.type !== 'video/mp4') {
        //     alert("Please upload a valid mp4 video file.");
        //     return;
        // }
        const formData = new FormData();
        formData.append('video', fileUploaded);
        try {
            const results = await axios.post('http://127.0.0.1:8000/split-video/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            console.log(results.data);
        }
        catch (error) {
            console.log(error);
        }
    }

    return (
        <div className='home'>
            <div className='video-upload' onDrop={handleDrop} onDragOver={handleDragOver}>
                <label className='upload-label' htmlFor='upload'>{fileUploaded ? fileUploaded.name : 'Upload a Video:'}</label>
                <input className='upload' id='upload' type="file" onChange={handleFileSelect} /> {/*accept="image/png, image/jpeg"*/}
            </div>
            <button className='split' onClick={splitVideo}> Split the video!</button>
        </div >
    )
}

export default Home;