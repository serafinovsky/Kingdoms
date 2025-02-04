import { MapEditor } from "../components/MapEditor"


export default function Maps() {
  return (
    <MapEditor 
    onSave={(map) => {
        console.log('Map saved:', map);
        // Send map to server or handle it as needed
    }} 
    />
  );
};

