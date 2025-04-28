#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
مدیریت تراکنش‌های بلاکچین BNB
این ماژول برای ارتباط با شبکه BNB و ارسال تراکنش‌ها استفاده می‌شود
"""

import os
import json
import random
import logging
from datetime import datetime
from web3 import Web3

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('blockchain_manager')

# آدرس کیف پول تستی 
TEST_WALLET_ADDRESS = "0x047fc8cbcc7fa4d715d7c4a0c05642248c6e8b70"

# آدرس‌های RPC تستی برای شبکه BNB تست‌نت
BNB_TESTNET_RPC_URLS = [
    "https://bsc-testnet.public.blastapi.io",
    "https://data-seed-prebsc-1-s1.binance.org:8545/",
    "https://data-seed-prebsc-2-s1.binance.org:8545/"
]

class BlockchainManager:
    """کلاس مدیریت تراکنش‌های بلاکچین BNB"""
    
    def __init__(self, private_key=None, wallet_address=None, rpc_url=None):
        """مقداردهی اولیه مدیریت بلاکچین"""
        # استفاده از RPC پیش‌فرض اگر مقدار ورودی نداریم
        if rpc_url is None:
            rpc_url = BNB_TESTNET_RPC_URLS[0]
        
        self.rpc_url = rpc_url
        self.web3 = self._connect_to_blockchain()
        
        # کلید خصوصی از محیط یا از پارامتر ورودی
        self.private_key = private_key or os.environ.get('BNB_PRIVATE_KEY')
        self.wallet_address = wallet_address or os.environ.get('BNB_WALLET_ADDRESS', TEST_WALLET_ADDRESS)
        
        logger.info(f"مدیریت بلاکچین راه‌اندازی شد با RPC: {rpc_url}")
    
    def _connect_to_blockchain(self):
        """اتصال به شبکه بلاکچین BNB"""
        try:
            web3 = Web3(Web3.HTTPProvider(self.rpc_url))
            
            # بررسی اتصال
            if web3.is_connected():
                logger.info(f"اتصال به شبکه BNB برقرار شد. شماره بلاک فعلی: {web3.eth.block_number}")
                return web3
            else:
                logger.error(f"خطا در اتصال به {self.rpc_url}")
                
                # تلاش با دیگر آدرس‌های RPC
                for alt_rpc in BNB_TESTNET_RPC_URLS:
                    if alt_rpc != self.rpc_url:
                        logger.info(f"تلاش برای اتصال به RPC جایگزین: {alt_rpc}")
                        web3 = Web3(Web3.HTTPProvider(alt_rpc))
                        if web3.is_connected():
                            self.rpc_url = alt_rpc
                            logger.info(f"اتصال به RPC جایگزین برقرار شد: {alt_rpc}")
                            return web3
                
                # اگر هیچ RPC کار نکرد
                raise ConnectionError("اتصال به هیچ RPC موفقیت‌آمیز نبود")
        
        except Exception as e:
            logger.error(f"خطا در اتصال به بلاکچین: {str(e)}")
            # در حالت دمو یک نمونه Web3 برمی‌گردانیم تا برنامه کار کند
            return Web3(Web3.HTTPProvider(self.rpc_url))
    
    def get_balance(self, address=None):
        """دریافت موجودی یک آدرس کیف پول"""
        try:
            address = address or self.wallet_address
            balance_wei = self.web3.eth.get_balance(address)
            balance_bnb = self.web3.from_wei(balance_wei, 'ether')
            logger.info(f"موجودی آدرس {address}: {balance_bnb} BNB")
            return balance_bnb
        except Exception as e:
            logger.error(f"خطا در دریافت موجودی: {str(e)}")
            return 0
    
    def get_network_info(self):
        """دریافت اطلاعات شبکه بلاکچین"""
        try:
            network_info = {
                "block_number": self.web3.eth.block_number,
                "gas_price": self.web3.from_wei(self.web3.eth.gas_price, 'gwei'),
                "chain_id": self.web3.eth.chain_id,
                "connected": self.web3.is_connected(),
                "rpc_url": self.rpc_url
            }
            return network_info
        except Exception as e:
            logger.error(f"خطا در دریافت اطلاعات شبکه: {str(e)}")
            return {
                "connected": False,
                "error": str(e)
            }
    
    def send_transaction(self, data=None, demo_mode=True):
        """ارسال تراکنش به شبکه بلاکچین

        در حالت دمو، تراکنش واقعی ارسال نمی‌شود و فقط اطلاعات نمایشی برگردانده می‌شود
        """
        # تولید عدد تصادفی 5 رقمی
        random_number = random.randint(10000, 99999)
        
        # زمان فعلی
        timestamp = datetime.now().isoformat()
        
        # داده‌های تراکنش (با عدد تصادفی)
        if data is None:
            data = {
                "random_number": random_number,
                "timestamp": timestamp,
                "message": "ارسال توکن از HosseinX4_bot"
            }
        
        # تبدیل به داده hex برای ارسال روی بلاکچین
        hex_data = self.web3.to_hex(text=json.dumps(data))
        
        try:
            if demo_mode or self.private_key is None:
                # حالت دمو - بدون ارسال تراکنش واقعی
                logger.info(f"حالت دمو: شبیه‌سازی ارسال تراکنش با داده: {data}")
                
                # ساخت یک هش تراکنش تصادفی
                fake_tx_hash = "0x" + "".join([random.choice("0123456789abcdef") for _ in range(64)])
                
                tx_result = {
                    "status": "success",
                    "tx_hash": fake_tx_hash,
                    "data": data,
                    "random_number": random_number,
                    "demo_mode": True,
                    "timestamp": timestamp,
                    "block_number": self.web3.eth.block_number if self.web3.is_connected() else 0,
                    "network": "BNB Testnet"
                }
                return tx_result
            
            else:
                # حالت واقعی - ارسال تراکنش به شبکه بلاکچین
                nonce = self.web3.eth.get_transaction_count(self.wallet_address)
                
                # ساخت تراکنش 
                tx = {
                    'to': self.wallet_address,  # ارسال به خود برای ثبت داده
                    'value': 0,  # بدون ارسال مقدار
                    'gas': 100000,
                    'gasPrice': self.web3.eth.gas_price,
                    'nonce': nonce,
                    'data': hex_data,
                    'chainId': self.web3.eth.chain_id
                }
                
                # امضای تراکنش
                signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
                
                # ارسال تراکنش
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                
                # دریافت رسید تراکنش
                receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
                
                tx_result = {
                    "status": "success" if receipt.status == 1 else "failed",
                    "tx_hash": tx_hash.hex(),
                    "block_number": receipt.blockNumber,
                    "gas_used": receipt.gasUsed,
                    "data": data,
                    "random_number": random_number,
                    "timestamp": timestamp,
                    "network": "BNB Testnet"
                }
                
                logger.info(f"تراکنش با موفقیت ارسال شد: {tx_result['tx_hash']}")
                return tx_result
                
        except Exception as e:
            logger.error(f"خطا در ارسال تراکنش: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "data": data,
                "random_number": random_number,
                "timestamp": timestamp,
                "demo_mode": demo_mode
            }


# تابع کمکی برای استفاده در Flask
def send_transaction_to_blockchain(user_id=None, username=None):
    """ارسال تراکنش به بلاکچین و دریافت نتیجه آن"""
    try:
        # ایجاد نمونه مدیریت بلاکچین
        blockchain_manager = BlockchainManager()
        
        # ساخت داده برای ارسال
        data = {
            "user_id": str(user_id) if user_id else "anonymous",
            "username": username or "کاربر ناشناس",
            "app": "HosseinX4_bot",
            "timestamp": datetime.now().isoformat()
        }
        
        # ارسال تراکنش در حالت دمو
        result = blockchain_manager.send_transaction(data=data, demo_mode=True)
        
        return result
    
    except Exception as e:
        logger.error(f"خطا در سرویس ارسال تراکنش: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# تست اولیه اگر فایل مستقیماً اجرا شود
if __name__ == "__main__":
    print("آزمایش سرویس بلاکچین...")
    
    # ایجاد یک نمونه آزمایشی
    blockchain = BlockchainManager()
    
    # نمایش اطلاعات شبکه
    network_info = blockchain.get_network_info()
    print(f"اطلاعات شبکه: {json.dumps(network_info, indent=2)}")
    
    # ارسال تراکنش آزمایشی
    result = blockchain.send_transaction(demo_mode=True)
    print(f"نتیجه تراکنش: {json.dumps(result, indent=2)}")