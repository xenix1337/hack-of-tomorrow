import { useEffect, useState, useCallback } from "react";
import './styles.css';

const LOCATION_NAMES = ["inn", "fairy_village"];
const PLAYER_ID = 0;

export default function App() {
    const [message, setMessage] = useState("");
    const [dialogue, setDialogue] = useState("");
    const [activeCharacter, setActiveCharacter] = useState(0);
    const [isSending, setIsSending] = useState(false);
    const [location, setLocation] = useState(0);
    const [agentsIds, setAgentsIds] = useState([]);

    const API_URL = import.meta.env.VITE_BACKEND_API_URL;

    const locationIdToResourceName = useCallback((id) => LOCATION_NAMES[id], []);

    const sendMessage = async (e) => {
        if (e.key === "Enter" && message.trim()) {
            setIsSending(true);
            try {
                const response = await fetch(`${API_URL}/say`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ player_id: PLAYER_ID, agent_id: activeCharacter, message: message }),
                });

                if (!response.ok) throw new Error(`Error: ${response.status}`);

                const data = await response.json();

                setDialogue(data.message);
                setActiveCharacter(data.responder_id);
                setMessage("");
            } catch (error) {
                console.error(error);
            } finally {
                setIsSending(false);
            }
        }
    };

    const enterLocation = async () => {
        try {
            const response = await fetch(`${API_URL}/enterLocation`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ player_id: PLAYER_ID, location_id: location }),
            });

            if (!response.ok) throw new Error(`Error: ${response.status}`);

            const data = await response.json();
            setAgentsIds(data.agents_ids);
            setActiveCharacter(data.agents_ids[0]);

        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        enterLocation();
    }, [location]);

    const changeLocation = () => {
        setLocation((prevLocation) => (prevLocation + 1) % LOCATION_NAMES.length);
        setDialogue("");
    }

    return (
        <div className="app-container"
            style={{ backgroundImage: `url('/images/${locationIdToResourceName(location)}/background.jpg')` }}>
            {dialogue && <div className="dialogue-box">{dialogue}</div>}
            <div className="content">
                {agentsIds.map((char, i) => (
                    <div key={char} className="column">
                        <img
                            src={`/images/${locationIdToResourceName(location)}/character_0${i + 1}.png`}
                            className={`character-img ${activeCharacter === char ? "talking" : ""}`}
                            alt="Character"
                            onClick={() => !isSending && setActiveCharacter(char)}
                        />
                    </div>
                ))}
            </div>
            <textarea
                className="input-box"
                placeholder="Type here..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={sendMessage}
                disabled={isSending}
            />
            <button
                className="change-location-button"
                onClick={changeLocation}
            >
                {location === 0 ? "Leave Inn" : "Go back to Inn"}
            </button>
        </div>
    );
}
