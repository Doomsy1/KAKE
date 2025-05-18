using UnityEngine;
using System.Collections.Generic;
using System.Text.RegularExpressions;

public enum ParseMode
{
    Calibration,
    Update
}

public class Calibration
{
    public int currentCalibrationCorner;
    public static Dictionary<int, (int, int)> cornerPositions = new Dictionary<int, (int, int)> {
        { 1, (0,0) },
        { 2, (1920, 0) },
        { 3, (0, 1080) },
        { 4, (1920, 1080) }
    };
    public bool expectedValue = true;

    public bool ReceiveRandomCalibration(string input)
    {
        if (expectedValue)
        {
            // Extract number from input, handling both formats: "0" and "[0]"
            string numberStr = input.Trim('[', ']', ' ');
            if (int.TryParse(numberStr, out int corner))
            {
                if (RecieveCalibrationCorner(corner))
                {
                    return true;
                }
            }
            else
            {
                Debug.LogError($"Failed to parse corner number from input: {input}");
            }
        }
        else
        {
            RecieveConfirmCalibration(input);
        }
        expectedValue = !expectedValue;
        return false;
    }

    public void RecieveConfirmCalibration(string agree)
    {
        Debug.Log($"Received confirmation: {agree}");
    }

    public bool RecieveCalibrationCorner(int corner)
    {
        Debug.Log($"Drawing calibration point at corner {corner}");
        currentCalibrationCorner++;
        if (currentCalibrationCorner == 5) return true;
        return false;
    }
}

public class ServerInfoParse : MonoBehaviour
{
    public static ServerInfoParse Instance { get; private set; }
    private ParseMode currentParseMode;
    private Calibration calibration;

    public void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(this);
        }
        else
        {
            Instance = this;
        }
        StartCalibration();
    }

    public void StartCalibration()
    {
        calibration = new Calibration();
        currentParseMode = ParseMode.Calibration;
        Debug.Log("Started calibration mode");
    }

    public void RecieveInput(string str)
    {
        Debug.Log($"Received input: {str}");
        
        if (currentParseMode == ParseMode.Calibration)
        {
            if (calibration.ReceiveRandomCalibration(str))
            {
                currentParseMode = ParseMode.Update;
                Debug.Log("Switched to Update mode");
            }
        }

        if (currentParseMode == ParseMode.Update)
        {
            Debug.Log("Processing update data");
        }
    }
} 