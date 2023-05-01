import React, { useState, useEffect } from 'react';
import { Text, View, StyleSheet, Button, Alert } from 'react-native';
import { BarCodeScanner } from 'expo-barcode-scanner';



export default function App() {
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);

  useEffect(() => {
    const getBarCodeScannerPermissions = async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    };

    getBarCodeScannerPermissions();
  }, []);

  const showConfirmationAlert = async (title, message) => {
    return new Promise((resolve, reject) => {
      Alert.alert(
        title,
        message,
        [
          { text: 'Yes', onPress: () => resolve(true) },
          { text: 'No', onPress: () => resolve(false) },
        ],
        { cancelable: false }
      );
    });
  };

  const handleBarCodeScanned = async ({ type, data }) => {
    setScanned(true);

    const confirmed = await showConfirmationAlert('Confirm', 'Will the device be destroyed here?');

    fetch('http://192.168.0.153:3000/message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: data + "=" + confirmed })
    })
      .then(response => response.text())
      .then(text => alert(text))
      .catch(error => console.error(error));

    // alert(`Bar code with type ${type} and data ${data} has been scanned!`);
  };

  if (hasPermission === null) {
    return <Text>Requesting for camera permission</Text>;
  }
  if (hasPermission === false) {
    return <Text>No access to camera</Text>;
  }

  return (
    <View style={styles.container}>
      <BarCodeScanner
        onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
        style={StyleSheet.absoluteFillObject}
      />
      {scanned && <Button title={'Tap to Scan Again'} onPress={() => setScanned(false)} />}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    flexDirection: 'column',
    justifyContent: 'center',
  },
});