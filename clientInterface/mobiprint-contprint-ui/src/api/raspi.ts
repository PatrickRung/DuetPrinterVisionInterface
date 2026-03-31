import axios, { AxiosError } from 'axios';

export const raspiAPIBaseURL = "/raspi";
export const raspiAPI = axios.create({
    baseURL: raspiAPIBaseURL,
});

/**
 * The other end of the API is formated in a json that contains data all on the same level
 * @param {String} data - The SVG contents as a string to send to backend.
 * @param {number} SVGWidth - Width of the SVG in CM.
 * @param {number} SVGHeight - The area of the rectangle.
 * @param {number} printBedWidth - Print bed w
 * @param {number} printBedHeight - The area of the rectangle.
 * @param {number} bedXOffsetCM - Width of the SVG in CM.
 * @param {number} bedYOffsetCM - The area of the rectangle.
 * @returns {JSON} Return Data - Return Json from the backend that should contain
 *                               multiple points 
 */
export const sliceData = async (data: string) => {
    return raspiAPI
        .post("/slice", { data })
        .then(({data}) => {
            return data;
        })
        .catch((error: AxiosError) => {
            if (error.response?.status === 400) {
                // Handle 400 Bad Request
                console.error("Bad request:", error.response.data);
                throw new Error("Invalid data provided");
            }
            throw error; // Re-throw other errors
        });
};