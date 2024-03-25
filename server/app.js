const { SkillBuilders } = require('ask-sdk-core');
const axios = require('axios');

const sheetId = "1hl3uC3BmTu7GNFF_ixkCuqn4apPNcVdOA53htNwZDIY";
const sheetName = "AllStudents";

const outputTypes = {
    "enrollment number": "Enrollment No.",
    "mobile number": "Student Phone No",
    "class": "Class",
    "email id": "Student gnu mail Id",
    "semester": "Semester",
    "batch": "Batch"
};

async function getStudentData(firstName, lastName = null, outputType = null) {
    let studentName = lastName ? `${lastName} ${firstName}` : firstName;
    let url = `https://script.google.com/macros/s/AKfycbwP3XOlI33GcQzZ1m7DWzt-CuwRy3YB8BBwGU_0lFf7KD56kUY/exec?spreadsheet=a&action=getbyname&id=${sheetId}&sheet=${sheetName}&sheetuser=${studentName}&sheetuserIndex=2`;

    try {
        const response = await axios.get(url);
        const data = response.data;

        if (data && data.hasOwnProperty('records')) {
            return data['records'];
        } else {
            return null;
        }
    } catch (error) {
        console.error("Error fetching student data:", error);
        return null;
    }
}

const GetStudentInfoIntentHandler = {
    canHandle(handlerInput) {
        return handlerInput.requestEnvelope.request.type === 'IntentRequest'
            && handlerInput.requestEnvelope.request.intent.name === 'GetStudentInfoIntent';
    },
    async handle(handlerInput) {
        const { firstName, lastName, outputType } = handlerInput.requestEnvelope.request.intent.slots;

        if (!firstName.value || !outputType.value) {
            const speakOutput = "Could not extract information from the request. Please try again.";
            return handlerInput.responseBuilder.speak(speakOutput).getResponse();
        }

        const studentData = await getStudentData(firstName.value, lastName.value, outputType.value);

        if (!studentData) {
            const speakOutput = `No data found for ${firstName.value} ${lastName.value}.`;
            return handlerInput.responseBuilder.speak(speakOutput).getResponse();
        }

        let speakOutput;
        if (studentData.length === 1) {
            speakOutput = `The ${outputType.value} is: ${studentData[0][outputTypes[outputType.value]]}`;
        } else {
            speakOutput = `Multiple records found for ${firstName.value} ${lastName.value}.`;
        }

        return handlerInput.responseBuilder.speak(speakOutput).getResponse();
    }
};

const skillBuilder = SkillBuilders.custom();
skillBuilder.addRequestHandlers(GetStudentInfoIntentHandler);

exports.handler = skillBuilder.lambda();
