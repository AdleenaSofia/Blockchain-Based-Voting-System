document.addEventListener("DOMContentLoaded", function () {

    const participants = JSON.parse('{{ participants | tojson | safe }}');
    const nonParticipants = JSON.parse('{{ non_participants | tojson | safe }}');


    
    // Populate Participants Table
    const participantsTable = document.getElementById('participantsTable');
    if (participantsTable) {
        participants.forEach(participant => {
            const row = `<tr>
                <td>${participant[0]}</td> <!-- Student ID -->
                <td>${participant[1]}</td> <!-- Name -->
                <td>${participant[2]}</td> <!-- Course -->
                <td>${participant[3]}</td> <!-- Semester -->
            </tr>`;
            participantsTable.innerHTML += row;
        });
    }

    // Populate Non-Participants Table
    const nonParticipantsTable = document.getElementById('nonParticipantsTable');
    if (nonParticipantsTable) {
        nonParticipants.forEach(nonParticipant => {
            const row = `<tr>
                <td>${nonParticipant[0]}</td> <!-- Student ID -->
                <td>${nonParticipant[1]}</td> <!-- Name -->
                <td>${nonParticipant[2]}</td> <!-- Course -->
                <td>${nonParticipant[3]}</td> <!-- Semester -->
            </tr>`;
            nonParticipantsTable.innerHTML += row;
        });
    }
});
