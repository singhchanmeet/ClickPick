import React, { useEffect, useState } from 'react';
import { View, Text, FlatList } from 'react-native';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import tw from 'twrnc'; // Import twrnc
 
const OrderScreen = () => {
    const [orders, setOrders] = useState([]);
    const url = "http://panel.mait.ac.in:8005"

    useEffect(() => {
        const fetchOrders = async () => {
            const accessToken = await AsyncStorage.getItem('access_token');
            try {
                const response = await axios.get(`${url}/stationery/active-orders/`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/json',
                    },
                });
                setOrders(response.data);
            } catch (error) {
                console.error('Error fetching orders:', error);
            }
        };

        fetchOrders();
    }, []);

    const renderItem = ({ item }) => (
        <View style={styles.orderItemContainer}>
            <Text style={styles.orderText}>{`Order ID: ${item.order_id}`}</Text>
            <Text style={styles.orderText}>{`Quantity: ${item.quantity}`}</Text>
            <Text style={styles.orderText}>{`Cost: $${item.cost}`}</Text>
            <Text style={styles.orderText}>{`Custom Message: ${item.custom_message}`}</Text>
            <Text style={styles.orderText}>{`Order Time: ${item.order_time}`}</Text>
            <Text style={styles.orderText}>{`User ID: ${item.user}`}</Text>
            <Text style={styles.orderText}>{`Item ID: ${item.item}`}</Text>
        </View>
    );

    return (
        <View style={styles.container}>
            <Text style={styles.heading}>Order Screen</Text>
            <FlatList
                data={orders}
                renderItem={renderItem}
                keyExtractor={(item) => item.order_id.toString()}
            />
        </View>
    );
};

const styles = {
    container: tw`flex-1 p-4 bg-gray-200`,
    heading: tw`text-2xl font-bold mb-4`,
    orderItemContainer: tw`bg-white rounded-lg p-4 mb-4`,
    orderText: tw`text-gray-500 mb-2`,
};

export default OrderScreen;
