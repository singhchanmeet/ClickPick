import {
    View,
    Text,
    FlatList,
    Image,
    SafeAreaView,
    TouchableOpacity,
    Alert,
} from 'react-native';
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import CustomButton from '../common/CommonButton';
import RazorpayCheckout from 'react-native-razorpay';
import { useNavigation } from '@react-navigation/native';
// import { RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET } from '@env'
import { addOrder } from '../redux/actions/Actions';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Checkout = () => {
    const cartData = useSelector(state => state.Reducers);
    console.log(cartData)
    const addressList = useSelector(state => state.AddressReducers);
    const dispatch = useDispatch();
    const navigation = useNavigation();
    const url = "http://panel.mait.ac.in:8005"; // Update with your API URL
    // let razorpayKeyId = RAZORPAY_KEY_ID
    // let razorpayKeySecret = RAZORPAY_KEY_SECRET

    console.log("Cart Data:", cartData);
    console.log("Address List:", addressList);
    const getTotal = () => {
        let tempTotal = 0;
        cartData.forEach(item => {
            // Convert the price string to a number and add it to tempTotal
            tempTotal += parseFloat(item.price) * item.quantity * 100; // Convert to paise
        });
        return tempTotal; // Return the total amount in paise as an integer
    };


    console.log("Total:", getTotal());

    return (
        <SafeAreaView style={{ flex: 1 }}>
            <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginTop: 20 }}>Checkout</Text>
                <View style={{ flex: 1, maxHeight: '90%' }}>
                    <FlatList
                        data={cartData}
                        renderItem={({ item, index }) => {
                            return (
                                <View
                                    style={{
                                        width: '100%',
                                        height: 70,
                                        flexDirection: 'row',
                                        marginTop: 10,
                                    }}>
                                    <Image
                                        source={{ uri: url + item.display_image }}
                                        style={{ width: 70, height: 70, marginLeft: 10 }}
                                    />
                                    <View style={{}}>
                                        <Text style={{ fontSize: 18 }}>{item.item}</Text>
                                        <Text style={{ marginTop: 5 }}>Quantity: <Text style={{ fontWeight: 'bold', color: '#000' }}>{item.quantity}</Text></Text>
                                        <Text style={{ marginTop: 5 }}>{'रु ' + item.price}</Text>
                                    </View>
                                </View>
                            );
                        }}
                    />

                </View>
                <View
                    style={{
                        flexDirection: 'row',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        paddingLeft: 20,
                        paddingRight: 20,
                        borderTopWidth: 0.5,
                        height: 50,
                        borderTopColor: '#8e8e8e',
                    }}>
                    <Text>Total :</Text>
                    <Text>{'रु ' + getTotal() / 100}</Text>
                </View>
                {/* <View>
                    <FlatList
                        data={addressList}
                        renderItem={({ item, index }) => {
                            return (
                                <View
                                    style={{
                                        width: '100%',

                                        borderWidth: 0.2,
                                        borderColor: '#8e8e8e',
                                        alignSelf: 'center',

                                        justifyContent: 'space-between',
                                        flexDirection: 'row',
                                        alignItems: 'center',
                                    }}>
                                    <View>
                                        <Text style={{ marginLeft: 20 }}>{'City: ' + item.city}</Text>
                                        <Text style={{ marginLeft: 20 }}>
                                            {'Building: ' + item.building}
                                        </Text>
                                        <Text style={{ marginLeft: 20, marginBottom: 10 }}>
                                            {'Pincode: ' + item.pincode}
                                        </Text>
                                    </View>
                                    <TouchableOpacity
                                        style={{ borderWidth: 0.2, padding: 7, marginRight: 20 }}
                                        onPress={() => {
                                            setSelectedAddress(
                                                'City :' +
                                                item.city +
                                                ' ' +
                                                ',Building: ' +
                                                item.building +
                                                ',Pincode: ' +
                                                item.pincode,
                                            );
                                        }}>
                                        <Text>Select address</Text>
                                    </TouchableOpacity>
                                </View>
                            );
                        }}
                    />
                </View> */}
                {/* <Text style={{ margin: 20, fontSize: 18 }}>Select Address</Text>
                <Text style={{ marginLeft: 20, fontSize: 16 }}>
                    {selectedAddress == ''
                        ? 'Please Select Address From Above List'
                        : selectedAddress}
                </Text> */}
                <View style={{ marginBottom: 100 }}>
                    <CustomButton
                        bgColor={'#000'}
                        textColor={'#fff'}
                        title={'Place Order'}
                        onPress={async () => {
                            const accessToken = await AsyncStorage.getItem('access_token');

                            var options = {
                                description: 'Buy items',
                                image: 'https://i.imgur.com/3g7nmJC.png',
                                currency: 'INR',
                                key: "rzp_test_1WhP3jEX0u7tb9",
                                amount: getTotal(),
                                name: 'test order',
                                order_id: "", // Replace this with an order_id created using Orders API.
                                prefill: {
                                    email: 'xyz@gmail.com',
                                    contact: '9999999999',
                                    name: 'User 1'
                                },
                                theme: { color: '#F37254' }
                            }

                            RazorpayCheckout.open(options).then(async (data) => {
                                // handle success
                                alert(`Success: ${data.razorpay_payment_id}`);

                                // Create order after successful payment
                                const orders = cartData.map(item => ({
                                    item: item.item,
                                    quantity: item.quantity,
                                    cost: parseFloat(item.price) * parseFloat(item.quantity),
                                    custom_message: ""
                                }));

                                console.log('Sending request to create order:', orders);

                                try {
                                    const response = await fetch(`${url}/stationery/create-order/`, {
                                        method: 'POST',
                                        headers: {
                                            'Authorization': `Bearer ${accessToken}`,
                                            'Content-Type': 'application/json',
                                        },
                                        body: JSON.stringify({ orders }),
                                    });

                                    console.log('Response status code:', response.status);

                                    if (response.ok) {
                                        const data = await response.json();
                                        console.log('Order created successfully:', data);
                                    } else {
                                        throw new Error('Failed to create order');
                                    }
                                } catch (error) {
                                    console.error('Error creating order:', error);
                                    // Handle error, e.g., show an alert
                                    Alert.alert('Error', 'Failed to create order. Please try again.');
                                }
                            }).catch((error) => {
                                // handle failure
                                console.log(error)
                                alert(`Error: ${error.code} | ${error.description}`);
                            });
                        }}
                    />
                </View>





            </View>
        </SafeAreaView>
    );
};

export default Checkout;
