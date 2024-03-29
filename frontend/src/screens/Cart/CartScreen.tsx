import { View, Text, FlatList, TouchableOpacity } from 'react-native';
import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addToWishlist, removeFromCart } from '../redux/actions/Actions';
import { useNavigation } from '@react-navigation/native';
import CartItem from '../common/CartItem';
import CommonButton from '../common/CommonButton';
 
const CartScreen = () => {
  const cartData = useSelector(state => state.Reducers);
  const dispatch = useDispatch();
  const navigation = useNavigation();
  const url = "http://panel.mait.ac.in:8005"
  return (
    <View style={{ flex: 1 }}>
       <Text style={{ fontSize: 24, fontWeight: 'bold', textAlign: 'center', marginTop: 20 }}>Your Cart</Text>
      {cartData.length > 0 ? (
        <FlatList style = {{marginTop : 40}}
          data={cartData}
          renderItem={({ item, index }) => {
            return (
              <CartItem
                url = {url}
                onAddWishlist={x => {
                  dispatch(addToWishlist(x));
                }}
                item={item}
                onRemoveItem={() => {
                  dispatch(removeFromCart(index));
                }}
              />
            );
          }}
        />
      ) : (
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <Text>No Items Added in Cart</Text>
        </View>
      )}
      {cartData.length > 0 ? (
        <View style={{ marginBottom: 100 }}>
          <CommonButton
            bgColor={'green'}
            textColor={'#fff'}
            title={'Checkout'}
            onPress={() => {
              navigation.navigate('Checkout');
            }}
          />
        </View>
      ) : null}
    </View>
  );
};

export default CartScreen;
