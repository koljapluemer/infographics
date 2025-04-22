// Import required Firebase functions
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, getDocs } from 'firebase/firestore/lite';
import fs from 'fs/promises';
import * as dotenv from 'dotenv';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

// Get current directory
const __dirname = dirname(fileURLToPath(import.meta.url));

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: process.env.FIREBASE_API_KEY,
  authDomain: process.env.FIREBASE_AUTH_DOMAIN,
  projectId: process.env.FIREBASE_PROJECT_ID,
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.FIREBASE_APP_ID
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

async function downloadCollection() {
  try {
    // Get reference to the collection
    const collectionRef = collection(db, "learning-data-webgame");
    
    // Get all documents from the collection
    const querySnapshot = await getDocs(collectionRef);
    
    // Convert the documents to a plain JavaScript object
    const data = {};
    querySnapshot.forEach((doc) => {
      data[doc.id] = doc.data();
    });
    
    // Write the data to a JSON file in the current directory
    const outputPath = join(__dirname, 'learning_data.json');
    await fs.writeFile(outputPath, JSON.stringify(data, null, 2));
    console.log(`Data successfully downloaded and saved to ${outputPath}`);
  } catch (error) {
    console.error('Error downloading data:', error);
    // Log more detailed error information
    if (error.code) {
      console.error('Error code:', error.code);
    }
    if (error.message) {
      console.error('Error message:', error.message);
    }
  }
}

// Run the download
downloadCollection(); 